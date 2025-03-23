from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request): 
    # return HttpResponse("<h4>Hello, world. You're at the main index.</h4>")
    return render(request, 'main/index.html')

def about(request): 
    # return HttpResponse("<h4>You're at the main about.</h4>")
    return render(request, 'main/about.html')