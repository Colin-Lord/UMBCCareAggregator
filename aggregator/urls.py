from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.home, name="home"),    
    path("contact/", views.contact, name="contact"),  
    path("dashboard/", views.dashboard, name="dashboard"),  
    path("data/", views.data, name="data"),    
    path("office/", views.office, name="office"),    
    path("users/", views.users, name="users"),
    path("single-record", views.upload_record, name="upload_record"),
    path("contact/success/", views.contact_success, name="contact_success") 


]