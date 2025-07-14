from django.contrib import admin
from .models import Medecin, Patient, Contact, Image_data, Utilisateur, Consultation,Interpretation

# Register your models here.
admin.site.register(Medecin)
admin.site.register(Patient)
admin.site.register(Contact)
admin.site.register(Image_data)
admin.site.register(Interpretation)
admin.site.register(Utilisateur)
admin.site.register(Consultation)
