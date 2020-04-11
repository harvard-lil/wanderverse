from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager

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


class Book(models.Model):
    author_last_name = models.CharField(max_length=64, null=True, blank=True)
    author_first_name = models.CharField(max_length=64, null=True, blank=True)
    publisher = models.CharField(max_length=128, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    isbn = models.CharField(max_length=16, null=True, blank=True)
    dewey_number = models.CharField(max_length=8, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET(
        0))  # setting to 0 rather than null so we can find and see if we want to delete it
    created_at = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}: {}, {}".format(self.title, self.author_last_name, self.author_first_name)


class Poem(models.Model):
    title = models.CharField(max_length=256, null=False, blank=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET(
        0))  # setting to 0 rather than null so we can find and see if we want to delete it
    created_at = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.title, self.created_at)


class Line(models.Model):
    text = models.TextField(blank=True, null=True)
    page = models.CharField(max_length=5, blank=True, null=True)
    book = models.ForeignKey(Book, related_name='book_lines', on_delete=models.SET(0))  # setting to 0 rather than null so we can find and see if we want to delete it
    poem = models.ForeignKey(Poem, related_name='poem_lines', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET(0))  # setting to 0 rather than null so we can find and see if we want to delete it
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        if len(self.text) > 50:
            return "{}[...]{}".format(self.text[:25], self.text[len(self.text) - 25:])
        else:
            return self.text

# an outline for what this might model look like if we do physical installations
# ROLE_CHOICES = [('Poet', 'poet'), ('Institutional Administrator', 'institutional_administrator'), ('Site Administrator', 'site_administrator')]
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
