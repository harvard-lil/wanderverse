import os
import json
import glob
import slack
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from slackbot import helpers

client = slack.WebClient(token=settings.SLACK_API_TOKEN)

ALLOWED_COMMANDS = {
    '*list*': 'list available commands `/wanderverse list`',
    '*new*': 'start new poem `/wanderverse new`',
    '*add*': 'add line to poem `/wanderverse add [your line here]`',
    '*show*': 'show last line of current poem `/wanderverse show`',
    '*get instructions*': 'get new instructions `/wanderverse get instructions`',
    '*unravel*': 'show entire poem `/wanderverse unravel`',
}


@csrf_exempt
def event_hook(request):
    print("getting request >>", request)

    response = {"type": "mrkdwn"}
    message = json.loads(request.body.decode())
    if 'event' in message and message['event']['type'] == 'message':
        if "<@U011U9SS4RJ>" in message['event']['text']:
            response = client.chat_postMessage(
                channel=message['event']['channel'],
                text="Hello world!\n I am a little bot that runs exquisite corpus poetry games.\n"
                     "Type `/wanderverse list` to get a list of available commands.")
            return HttpResponse("ok")
    if 'challenge' in message:
        response['challenge'] = message['challenge']
    return JsonResponse(response, safe=False)


@csrf_exempt
def slash_command(request):
    print(request.POST)
    command = request.POST.get('text')
    response = {"type": "mrkdwn"}
    list_of_files = glob.glob(settings.SLACK_STORAGE + "/*.txt")

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
    else:
        latest_file = None
    if command == 'list':
        response_string = ""
        for c in ALLOWED_COMMANDS:
            response_string += "- " + c + ": " + ALLOWED_COMMANDS[c] + "\n"
        response["text"] = response_string

    elif command == "show":
        if latest_file:
            with open(latest_file, "r") as f:
                lines = f.readlines()
            if len(lines):
                response["text"] = "*This is the last line* (the rest will remain hidden until you unravel):\n\n\n"
                response["text"] += "--------------------------\n\n"
                response["text"] += lines[-1]
                response["text"] += "\n\n--------------------------"
            else:
                response[
                    "text"] = "This poem hasn't been started yet. Add a first line by writing `/wanderverse add [your line]`"
        else:
            response["text"] = "No poems to show. To start a new one, type `/wanderverse new`"
    elif command[0:3] == "add":
        if latest_file:
            with open(latest_file, "a") as f:
                f.write("\n" + command[4:])
        else:
            newfile = str(datetime.today()) + ".txt"
            with open(newfile, "a+") as f:
                f.write(command[4:])
        if settings.SLACK_ANNOUNCE:
            client.chat_postMessage(
                channel=settings.SLACK_CHANNEL,
                text="A new line has been added to the latest poem. Type `/wanderverse show` to get a peek.")
        response["text"] = "added your line. Thank you for playing!"
    elif command[0:3] == "new":
        newfile = os.path.join(settings.SLACK_STORAGE, str(datetime.today()) + ".txt")
        newfileobj = open(newfile, "w+")
        response["text"] = "Created a new poem. Type `/wanderverse add` followed by your line"
        if settings.SLACK_ANNOUNCE:
            client.chat_postMessage(
                channel=settings.SLACK_CHANNEL,
                text="A new exquisite game is afoot! Join by typing `/wanderverse list` to see available commands")

    elif command == "unravel":
        if latest_file:
            with open(latest_file, "r") as f:
                response["text"] = "--------------------------\n"
                response["text"] += f.read()
                response["text"] += "\n\n--------------------------"
        else:
            response["text"] = "No poems to show. To start a new one, type `/wanderverse new`"
    elif command == "get instructions":
        response["text"] = helpers.get_instructions()
        if latest_file:
            with open(latest_file, "r") as f:
                lines = f.readlines()
            if len(lines):
                response["text"] += "\n\n*This is the last line* (the rest will remain hidden until you unravel):\n\n\n"
                response["text"] += "--------------------------\n\n"
                response["text"] += lines[-1]
                response["text"] += "\n\n--------------------------"
    else:
        response[
            "text"] = "Uh oh! I didn't understand that command. Type `/wanderverse list` to see available commands."
    return JsonResponse(response, safe=False)
