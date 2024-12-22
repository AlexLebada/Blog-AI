from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta: # this class is modifying the inherited parent class
        model = User
        # establish the displaying order of form fields
        fields = ["username", "email", "password1", "password2"]
