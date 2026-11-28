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
    if request.user.office:
        office_name = request.user.office.name
    else:
        office_name = ""

    metrics = OFFICE_METRICS.get(office_name, {})

    if request.method == "POST":
        period_start = request.POST.get("period_start")
        period_end = request.POST.get("period_end")
        student_level = request.POST.get("student_level")
        metric = request.POST.get("metric")
        value = request.POST.get("value")

        # Check if metric belongs to the user's office
        if metric not in metrics:
            messages.error(request, "Invalid metric for your office.")
            return redirect("upload_record")

        # Automatically retrieve the corresponding unit
        unit = METRIC_UNITS[metric]

    context = {
        "metrics": metrics,
    }
    return render(request, "aggregator/record.html", context)


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


# used to show metrics for the individual data upload
OFFICE_METRICS = {
    "Retriever Essentials": {
        "service_interactions": "Service Interactions",
        "unique_students": "Unique Students",
        "referrals_made": "Referrals Made",
        "food_distributed_lb": "Food Distributed (lb)",
    },

    "Retriever CARE": {
        "students_assisted": "Students Assisted",
        "care_referrals_received": "CARE Referrals Received",
        "case_management_meetings": "Case Management Meetings",
        "cases_resolved": "Cases Resolved",
    },

    "Pride Center": {
        "center_visits": "Center Visits",
        "event_attendance": "Event Attendance",
        "lgbtq_programs_hosted": "LGBTQ+ Programs Hosted",
        "student_satisfaction": "Student Satisfaction",
    },

    "Mosaic Center": {
        "center_visits": "Center Visits",
        "cultural_programs_hosted": "Cultural Programs Hosted",
        "event_attendance": "Event Attendance",
        "diversity_and_inclusion_workshops": "Diversity and Inclusion Workshops",
    },

    "Graduate Student Life": {
        "graduate_student_participation": "Graduate Student Participation",
        "professional_development_workshops": "Professional Development Workshops",
        "graduate_student_events_hosted": "Graduate Student Events Hosted",
        "student_satisfaction": "Student Satisfaction",
    },
}

# used to show a metric's corresponding units for the individual data upload
METRIC_UNITS = {
    # Retriever Essentials
    "service_interactions": "interactions",
    "unique_students": "students",
    "referrals_made": "referrals",
    "food_distributed_lb": "lb",

    # Retriever CARE
    "students_assisted": "students",
    "care_referrals_received": "referrals",
    "case_management_meetings": "meetings",
    "cases_resolved": "cases",

    # Pride Center
    "center_visits": "visits",
    "event_attendance": "attendees",
    "lgbtq_programs_hosted": "programs",
    "student_satisfaction": "percentage",

    # Mosaic Center
    "cultural_programs_hosted": "programs",
    "diversity_and_inclusion_workshops": "workshops",

    # Graduate Student Life
    "graduate_student_participation": "students",
    "professional_development_workshops": "workshops",
    "graduate_student_events_hosted": "events",
}