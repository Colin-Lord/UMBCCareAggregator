from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError

from .forms import DataUploadForm
from .imports import can_upload, import_records
from .models import DataImport, MetricRecord

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
    allowed = can_upload(request.user)
    form = DataUploadForm()
    if request.method == 'POST':
        if not allowed:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('An authorized office account is required to upload data.')
        form = DataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                batch = import_records(form.records, request.user, form.cleaned_data['json_file'].name)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, f'Import complete: {batch.created_count} records added and {batch.updated_count} existing records updated.')
                return redirect('data')
    records = MetricRecord.objects.none()
    imports = DataImport.objects.none()
    if request.user.is_authenticated:
        records = MetricRecord.objects.select_related('office')
        imports = DataImport.objects.select_related('uploaded_by')
        if not request.user.is_superuser:
            records = records.filter(office_id=request.user.office_id) if request.user.office_id else records.none()
            imports = imports.filter(uploaded_by=request.user)
    return render(request, 'aggregator/data.html', {
        'form': form, 'can_upload': allowed, 'record_count': records.count(),
        'records': records[:50], 'imports': imports.order_by('-uploaded_at')[:10],
    })

def office(request):
    return render(request, "aggregator/office.html")

def login(request):
    return render(request, "accounts/login.html")

def users(request):
    return render(request, "aggregator/users.html")
