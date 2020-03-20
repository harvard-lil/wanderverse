from django.shortcuts import render

# Create your views here.
def index(request):
    print("index called")
    return render(request, 'index.html')

