from django.shortcuts import render, redirect
from django.http import HttpResponse
from csv import DictReader, DictWriter
from json import loads
from aggregator.models import CSVFile, DataRecord, MetricValue, User, Office, Metric
from django.contrib.auth.decorators import login_required
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

@login_required
def data(request):
    if request.method == "POST":
        uploaded = request.FILES.get("csv_file")

        if uploaded:
            try:
                records = process_upload(uploaded)
                if validate_data(records, request.user): #validate data
                    print("Data is valid!")

                    #TODO Convert data into models on the database if valid
                    data_to_model(records, request.user)
                    

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


def TEST_setup_models(user):
    #this function is only used to setup tables in order to test data validation
    #use `python manage.py flush` before this to clear all data

    #create office and assign to logged in user
    new_office = Office(name = "Retriever Essentials")
    new_office.save()
    user.office = new_office
    user.save()

    users_office = user.office

    #create metrics and assign to user's  office
    metrics_to_add = ["record_id","office_id","office_name","period_start","period_end","student_level","metric","value","unit"]
    for metric_o_o in metrics_to_add:
        new_metric = Metric(name=metric_o_o)
        new_metric.save()
        new_metric.offices.set([users_office])


#TODO make it so the standard columns (record_id, office_id, etc) aren't treated as office specific metrics.
#TODO essentially only check if the value in the metric column matches a metric in that office

#TODO the current way this validates is not correct

def validate_data(data, user):
    #run once to set up test data
    #TEST_setup_models(user)
    
    #loop through data records
    for record in data:

        #invalid if the number of metrics don't match
        if len(list(user.office.metrics.all())) != len(list(record)):
            print("INVALID DATA. invalid number of metrics")
            return False

        #invalid if a metric from office is not in the data
        for metric in list(user.office.metrics.all()):
            if metric.name not in list(record):
                print("INVALID DATA. " + metric.name + " not in file.")
                return False

   
    # if it made it through everything, the data is valid
    return True

def data_to_model(data, user):
    #this function should only be called if data is already validated


    new_file = CSVFile(filename="testname",office = user.office, user=user)
    new_file.save()

    office_metrics = list(user.office.metrics.all())

    for record in data:
        new_record = DataRecord(timeframe="1969-01-01",csv_file = new_file)
        new_record.save()

        for key in list(record):
            
            #TODO extremely inefficient, refactor later
            for office_metric in office_metrics:
                if key == office_metric.name:
                    assign_metric = office_metric


            new_value = MetricValue(value = record[key], data_record = new_record, metric = assign_metric)
            new_value.save()

    print(new_file.filename + " saved!")
