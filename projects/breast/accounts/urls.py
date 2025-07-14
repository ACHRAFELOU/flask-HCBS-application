from django.urls import path
from . import views
urlpatterns = [
       path("registre", views.registre, name ="registre")

]