from django.contrib import admin
from .models import Contact, Image, Interprétation, Médecin,Patient, Utilisateur
# Register your models here.
admin.site.register(Contact)
admin.site.register(Image)
admin.site.register(Interprétation)
admin.site.register(Médecin)
admin.site.register(Patient)
admin.site.register(Utilisateur)
