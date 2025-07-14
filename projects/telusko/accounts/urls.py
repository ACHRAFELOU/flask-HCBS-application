from django.urls import path
from . import views
urlpatterns=[

    path("Inscription_Patient", views.Inscription_Patient,name="Inscription_Patient"),
    path("login", views.login,name="login")
]