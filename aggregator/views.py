from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the aggregator index.")

def home(request):
    return render(request, "aggregator/home.html")

def contact(request):
    return render(request, "aggregator/contact.html")

def dashboard(request):
    return render(request, "aggregator/dashboard.html")

def data(request):
    return render(request, "aggregator/data.html")

def office(request):
    return render(request, "aggregator/office.html")

def login(request):
    return render(request, "aggregator/login.html")