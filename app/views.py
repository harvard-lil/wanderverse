from django.shortcuts import render

def index(request):
    print("index called")
    return render(request, "index.html")

def verse(request):
    return render(request, "verse.html")