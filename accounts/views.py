from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AggregatorUserCreationForm


class SignUpView(CreateView):
    form_class = AggregatorUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"