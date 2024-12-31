from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.contrib.auth.models import Group


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            # save user in db
            user = form.save()
            group = Group.objects.get(name='Readers')
            user.groups.add(group)

        return redirect("/")
    else:
        form = RegisterForm()

    return render(response, "register/register.html", {"form":form})