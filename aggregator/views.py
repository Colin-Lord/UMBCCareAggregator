from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the aggregator index.")

def home(request):
    return render(request, "aggregator/home.html")

def contact(request):
    if request.method == "POST":
        feedback = request.POST.get("feedback")

        # TODO: Save feedback to database or send email

        return redirect("contact_success")

    return render(request, "aggregator/contact.html")

def contact_success(request):
    return render(request, "aggregator/contact_success.html")

def dashboard(request):
    return render(request, "aggregator/dashboard.html")

def data(request):
    return render(request, "aggregator/data.html")

def upload_record(request):
    return render(request, "aggregator/record.html")

def office(request):
    return render(request, "aggregator/office.html")

def login(request):
    return render(request, "accounts/login.html")

def users(request):
    return render(request, "aggregator/users.html")