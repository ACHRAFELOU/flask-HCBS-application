"""hope URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from base_app import views
from django.conf.urls import url

urlpatterns = [
    path('', views.accueil, name="accueil"),
    path('inscription', views.inscription, name="inscription"),
    path('se_connecter', views.se_connecter, name="se_connecter"),
    # path('apres_connection_medecin', views.apres_connection_medecin, name="apres_connection_medecin"),
    path('apres_inscription', views.apres_inscription, name="apres_inscription"),
    path('Medformpage', views.Medformpage, name="Medformpage"),
    path('Patformpage', views.Patformpage, name="Patformpage"),
    path('deconnecter', views.logout, name="deconnecter"),
    path('connection', views.se_connecter, name="connection"),
    path('show_graph', views.show_graph, name="show_graph"),
    # path('DoctorProfile', views.DoctorProfile, name="DoctorProfile"),
    path('fetch_sensor_values_ajax', views.fetch_sensor_values_ajax, name="fetch_sensor_values_ajax"),
    path('fetch_saved_sensor_values_ajax', views.fetch_saved_sensor_values_ajax, name="fetch_saved_sensor_values_ajax"),
    path('show_thermal', views.show_thermal, name="show_thermal"),
    path('fetch_termal_image_ajax', views.fetch_termal_image_ajax, name="fetch_termal_image_ajax"),
    path('Consultation_patient', views.Consultation_patient, name="Consultation_patient"),
    path('Connection_Patient', views.Connection_Patient, name="Connection_Patient"),
    path('Connection_Doctor', views.Connection_Doctor, name="Connection_Doctor"),
    path('Connection_historique/<str:global_id_user>', views.Connection_historique, name="Connection_historique"),
    path('Calender_date', views.Calender_date, name="Calender_date"),
    path('create_Consultation', views.create_Consultation, name="create_Consultation"),
    path('Interpretformpage', views.Interpretformpage, name="Interpretformpage"),

    # url(r'^Connection_historique/(?P<user_id>\d+)/$', views.Connection_historique, name='Connection_historique'),
]
