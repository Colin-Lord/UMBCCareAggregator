from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),    
    path("contact/", views.contact, name="contact"),  
    path("dashboard/", views.dashboard, name="dashboard"),  
    path("data/", views.data, name="data"),    
    path("office/", views.office, name="office"),    
    path("login/", views.login, name="login"),
    path("users/", views.users, name="users"),
    path("contact/success/", views.contact_success, name="contact_success")  
]