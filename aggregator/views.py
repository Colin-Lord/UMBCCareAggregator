from django.shortcuts import render, redirect
from django.http import HttpResponse
from csv import DictReader, DictWriter
from json import loads
from django.contrib import messages
from .models import Office, User, CSVFile, DataRecord, Metric, MetricValue

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
    if request.method == "POST":
        uploaded = request.FILES.get("csv_file")

        if uploaded:
            try:
                records = process_upload(uploaded)

                for record in records:

                    # TODO: this code prints all the dictionaries created by the file; delete or comment out later
                    print(record, "\n\n")
                    

            # TODO: make this code display an error message on the Data page
            except (ValueError, UnicodeDecodeError) as e:
                print(f"Upload error: {e}")

    return render(request, "aggregator/data.html")

def upload_record(request):
    return render(request, "aggregator/record.html")


def office(request):
    members = User.objects.filter(
        office=request.user.office
    )

    return render(request, "aggregator/office.html", {"members": members})

def login(request):
    return render(request, "accounts/login.html")

def users(request):

    # deal with user deletion or level editing if submit was pressed
    if request.method == "POST":
        action = request.POST.get("action")
        username = request.POST.get("username")
        level = request.POST.get("level")

        try:
            account = User.objects.get(username=username)

            if action == "delete":
                account.delete()
                messages.success(request, "User deleted successfully.")

            elif action == "edit":
                if level in ["staff", "director", "admin"]:
                    account.level = level
                    account.save()
                    messages.success(request, "User level updated successfully.")
                else:
                    messages.error(request, "Invalid user level.")

            else:
                messages.error(request, "Invalid action.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    # get the criteria to sort the users by
    sort_by = request.GET.get("sort", "username")
    sort_options = {
        "name": "username",
        "email": "email",
        "office": "office__name",
        "level": "level",
    }

    # sort the users, default is username
    order = sort_options.get(sort_by, "username")

    all_users = User.objects.all().order_by(order)

    return render(request, "aggregator/users.html", {"users": all_users})


# function to process the data upload
def process_upload(uploaded):
    content = uploaded.read().decode("utf-8-sig")

    # get a list of dictionaries from a CSV, if that was the file type
    if uploaded.name.lower().endswith(".csv"):
        reader = DictReader(content.splitlines())
        return list(reader)

    # get a list of dictionaries from a JSON, if that was the file type
    elif uploaded.name.lower().endswith(".json"):
        data = loads(content)
        return data

    else:
        raise ValueError("Unsupported file type")