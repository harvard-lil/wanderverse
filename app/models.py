import random
import re
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager

from profanity_check import predict as profanity_predict
from Phyme import Phyme
import syllables

ROLE_CHOICES = [('Poet', 'poet'), ('Site Administrator', 'site_administrator')]


class Country(models.Model):
    name = models.TextField(null=True)
    code = models.TextField(null=True, max_length=254)
    has_postal_codes = models.BooleanField(default=False)


class SiteUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='poet', null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    postal_code = models.CharField(max_length=12, blank=True)
    display_name = models.CharField(max_length=24, unique=True, blank=False)
    country = models.ForeignKey(Country, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    is_suspended = models.BooleanField(default=False)
    is_shadow_suspended = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    objects = UserManager()

    def __str__(self):
        return "{}({})".format(self.email, self.display_name)


class Poem(models.Model):
    title = models.CharField(max_length=256, null=False, blank=False)
    # setting to 0 rather than null so we can find and see if we want to delete it
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET(0))
    created_at = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True)
    lock_code = models.CharField(max_length=128, null=True)
    unraveled = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    @staticmethod
    def get_poem_and_lock_code(poem_id=None, lock_code=None, user_id=None):
        """ Get a poem by lock code, then pk, include a lock code if necessary. If there's no pk included, get a
        random poem. Failing that, create a new one. """
        poem = None
        status = None

        # if we're trying to get a specific poem
        if poem_id:
            try:
                poem = Poem.objects.get(pk=poem_id)
                if not poem.check_lock_permissions(lock_code):
                    return 'already_locked', lock_code, poem
                status = "retrieved" if poem else None
            except ObjectDoesNotExist:
                pass

        # no ID, but the user might be revisiting or refreshing. Let's try to get them the same poem
        if not poem and lock_code:
            try:
                poem = Poem.objects.get(lock_code=lock_code)
                status = "returning" if poem else None
            except ObjectDoesNotExist:
                pass

        # if none of that was the case, let's try and get them a random unlocked poem
        if not poem:
            poem = Poem.get_random_unlocked_poem()
            status = "random" if poem else None

        # If no poem is available, start a new one
        if not poem:
            poem = Poem()
            poem.created_by = user_id
            status = "created" if poem else None

        poem.lock_code = get_random_string(length=32)
        poem.locked_at = timezone.now()
        poem.save()
        return status, lock_code, poem

    @staticmethod
    def get_random_finished_poem():
        """ TODO: Determine if viewing a poem is significantly different enough from contributing to a poem that
         it needs different views/etc. """
        try:
            poem_id = random.choice(Poem.objects.filter(unraveled=True).values_list('id', flat=True))
        except IndexError:
            raise Exception("No Finished Poems in Database")
        return Poem.objects.get(pk=poem_id)

    @staticmethod
    def get_random_unlocked_poem():
        """ This should be the primary way for a user to get a random poem to contribute to """
        lock_limit = timezone.now() - timedelta(hours=settings.LOCK_TIME_LIMIT)
        tries = 0
        poem_count = Poem.objects.count()
        if not poem_count:
            Poem.objects.create()
            poem_count = 1
        while tries < 100:
            tries += 1
            try:
                poem = Poem.objects.get(pk=random.choice(range(1, poem_count + 1)))
                if not poem.locked_at or poem.locked_at < lock_limit:
                    return poem
            except ObjectDoesNotExist:
                pass

    def add_line_and_unlock(self, lock_code, poem_id, verse_content, verse_metadata, user_id=None):
        """ This should be the primary line-adding method """
        if not self.check_lock_permissions(lock_code):
            return "already_locked", ["Poem is already locked by another session. "
                                      "Try again after {} Eastern Time".format(poem.locked_at)]
        status, details = Verse.check_and_create(verse_content, verse_metadata, self, user_id)
        if status == "profanity":
            return status, details
        self.unlock(lock_code)
        return status, details

    def unlock(self, lock_code=None, override_lock=False):
        """ Unlocks if the lock_code has permission, or is forced """
        if self.check_lock_permissions(lock_code) or override_lock:
            self.lock_code = None
            self.locked_at = None
            self.save()

    def check_lock_permissions(self, lock_code):
        """ Checks to see if the provided lock_code gives access to this poem"""
        lock_limit = timezone.now() - timedelta(hours=settings.LOCK_TIME_LIMIT)
        if lock_code == self.lock_code or self.locked_at > lock_limit:
            return True
        else:
            return False

    def get_preview_verses(self):
        """ returns a list with the last two lines, and also a list that we could opt to give users another hint with,
        like last_word_rhyme and number of syllables """
        verses = self.poem_verses.all()
        verses_count = verses.count()
        hints = []
        full_lines = []
        if verses_count > 2:
            i = 1
            for verse in verses:
                if i > verses_count - 2:
                    full_lines.append(verse)
                else:
                    hints.append(verse)
                i += 1
        else:
            full_lines = verses
        return full_lines, hints

    def __str__(self):
        return "{} ({})".format(self.title, self.created_at)


class Verse(models.Model):
    text = models.TextField(blank=True, null=True)
    poem = models.ForeignKey(Poem, related_name='poem_verses', on_delete=models.CASCADE)
    # setting to 0 rather than null so we can find and see if we want to delete it
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET(0))
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    metadata = JSONField(null=True)
    syllables = models.IntegerField(default=0)
    last_word_rhyme = models.CharField(max_length=64, null=True)

    def __str__(self):
        if len(self.text) > 50:
            return "{}[...]{}".format(self.text[:25], self.text[len(self.text) - 25:])
        else:
            return self.text

    def save(self, *args, **kwargs):
        """ This is only overridden so the rhyming and syllable analysis happens. If we scrap that, we can scrap this """
        self.syllables = syllables.estimate(self.text)
        split_sentence = re.sub('[\W_]+', ' ', self.text).split()
        if len(split_sentence) == 0:
            raise Exception("Verse must contain words.")
        last_word = split_sentence[-1]
        ph = Phyme()
        try:
            last_word_rhymes = ph.get_perfect_rhymes(last_word)
            self.last_word_rhyme = last_word_rhymes[list(last_word_rhymes.keys())[0]][0]
        except KeyError:
            self.last_word_rhyme = last_word

        return super(Verse, self).save(*args, **kwargs)

    @staticmethod
    def check_and_create(verse_content, verse_metadata, poem, user_id):
        """ Checks the metadata and poem text for profanity, then creates it. """
        profanity = []
        profanity += [verse_content] if 1 in profanity_predict([verse_content]) else []
        profanity += [(item[0], item[1]) for item in verse_metadata if 1 in profanity_predict([item[0], item[1]])]

        if not profanity:
            verse = Verse()
            verse.text = verse_content
            verse.poem = poem
            verse.metadata = verse_metadata
            if user_id:
                verse.created_by = user_id
            verse.save()
            verse.refresh_from_db()
            return "ok", verse.pk
        else:
            return "profanity", profanity

# an outline for what this might model look like if we do physical installations
# ROLE_CHOICES = [('Poet', 'poet'), ('Institutional Administrator', 'institutional_administrator'),
# ('Site Administrator', 'site_administrator')]
# class Institution(models.Model):
#    full_name = models.TextField()
#    short_name = models.TextField(max_length=32)
#    country = models.ForeignKey(Country, null=True)
#    postal_code = models.TextField(max_length=12)
#    created_at = models.DateTimeField(auto_now_add=True)
#    on_site_only = models.BooleanField(default=False)
# class User(AbstractUser):
# ...
#    institution = models.ForeignKey(Institution, null=True)

#    def has_institutional_admin_jurisdiction(self, institution):
#        return True if institution == self.institution and self.role == 'institutional_administrator' else False
