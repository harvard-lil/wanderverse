from django.shortcuts import render, redirect
from app.models import Poem
from django.http import HttpResponseNotAllowed


def index(request):
    return render(request, "index.html")


def read_poem(request, poem_id=None):
    poem = None
    if poem_id:
        poem = Poem.objects.get(pk=poem_id)
    if not poem:
        poem = Poem.get_random_finished_poem()
    return render(request, "read.html", {
        'poem': poem
    })


def read_poems(request):
    # TODO: create or scrap this? Should this just be on the homepage?
    return render(request, "list.html")


def add_line(request, poem_id):
    """ Adds a line to a poem """
    if request.method != 'POST':
        return redirect('read', poem_id)

    lock_code = request.session.get('lock_code', None)
    if not lock_code:
        #TODO: Message for users that don't have cookies enabled?
        return redirect('contribute', poem_id)

    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        user_id = None

    if 'verse' not in request.POST:
        #TODO appopriate response to validation errors
        return redirect('read', poem_id)

    metadata = {}
    for fieldname in request.POST.keys():
        if fieldname.startswith('metadata_key_'):
            field_number = fieldname.split("metadata_key_")[1]
            field_key_name = fieldname
            field_value_name = "metadata_value_{}".format(field_number)
            if field_key_name in request.POST and field_value_name in request.POST:
                field_key = request.POST[field_key_name]
                field_value = request.POST[field_value_name]
                if field_key and field_value:
                    metadata[field_key] = field_value
    status, _lock_code, poem = Poem.get_poem_and_lock_code(poem_id, request.session.get('lock_code', None), user_id=user_id)


    if status == 'retrieved':
        line_status, line_details = poem.add_line_and_unlock(request.session.get('lock_code', None), poem_id,
                                                             request.POST['verse'], metadata, user_id=None)
        if line_status == 'profanity':
            # TODO appopriate response to validation errors
            return redirect('read', poem_id)
    else:
        # At this stage we should only be getting 'retrieved' as a status. The other things, such as getting a random
        # poem or creating a new one, should have been completed when they visited the 'contribute' screen.
        # TODO appopriate response to validation errors
        return redirect('read', poem_id)


    return redirect('read', poem_id)


def contribute(request, poem_id=None):
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        user_id = None
    status, lock_code, poem = Poem.get_poem_and_lock_code(poem_id, request.session.get('lock_code', None), user_id=user_id)
    # TODO: also can return "retrieved" "returning" "random" and "created". Maybe want to have a customized message
    # telling user what's happening?
    if status == 'already_locked':
        #TODO appopriate response to validation errors
        return redirect('read', poem_id)

    last_two_verse_objects, previous_verse_objects = poem.get_preview_verses()
    previews = []
    for verse in previous_verse_objects:
        previews.append("A verse with {} syllables that ends in a word that rhymes with {}".format(
            verse.syllables, verse.last_word_rhyme))
    for verse in last_two_verse_objects:
        previews.append(verse.text)

    return render(request, "contribute.html", {
        "poem": poem,
        "previews": previews,
        "lock_code": lock_code,
        "status": status
    })
