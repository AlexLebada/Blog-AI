from django.contrib import admin
from django.urls import path, include
from register import views as register_views

urlpatterns = [
    path('', register_views.register, name="register"),
]