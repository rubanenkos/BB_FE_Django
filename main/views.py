from django.shortcuts import render
from django.http import HttpResponse
import requests

# Create your views here.
def index(request): 
    return render(request, 'main/index.html')

def about(request): 
    return render(request, 'main/about.html')

def users(request):
    response = requests.get('http://127.0.0.1:5000/donors')
    donors = response.json()
    return render(request, 'main/users.html', {'donors': donors})

def contacts(request): 
    return render(request, 'main/contacts.html')