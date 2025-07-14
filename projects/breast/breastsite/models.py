from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

spécialité_types = [
    ('spa',"Aucune"),
    ('spb',"chirurgien"),
    ('spc',"Cancérologue"),
    ('spd',"Gynécologue")
]

sex_types = [
    ('1','Homme'),
    ('2','Femme'),
]

quartier_types = [
    ('0', ' '),
    ('1', 'Hay Riad'),
    ('2', 'Hassan 2'),
    ('3', 'Agdal')
]

img_types = [
    ('1', 'PNG'),
    ('2', 'JPEG'),
    ('3', 'JFIF'),
]

class Médecin(models.Model):
    nom = models.CharField("Nom ",max_length=30)
    prénom = models.CharField("Prénom ", max_length=30)
    cin = models.CharField("C.I.N ", max_length=10)
    date_de_naissance = models.DateField(null=True, blank=True)
    spécialité = models.CharField(max_length=20, choices=spécialité_types, default='spa')
    sexe = models.CharField(max_length=10, choices=sex_types, default='1')
    quartier = models.CharField(max_length=20, choices=quartier_types, default='0')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.prénom + ' ' + self.nom


class Patient(models.Model):
    nom = models.CharField("Nom ",max_length=30)
    prénom = models.CharField("Prénom ", max_length=30)
    cin = models.CharField("C.I.N ", max_length=10)
    date_de_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=10, choices=sex_types, default='1')
    quartier = models.CharField(max_length=20, choices=quartier_types, default='0')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.prénom + ' ' + self.nom


class Contact(models.Model):
    nom = models.CharField("Nom", max_length=30)
    prénom = models.CharField("Prénom ", max_length=30)
    email = models.EmailField("Email ", max_length=30)
    message = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.prénom + ' ' + self.nom


class Image(models.Model):
    nom_patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    nom_médecin = models.ForeignKey(Médecin, on_delete=models.CASCADE)
    type_img = models.CharField(max_length=10, choices=img_types, default='1')
    date_de_création = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_patient


class Interprétation(models.Model):
    nom_patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    nom_médecin = models.ForeignKey(Médecin, on_delete=models.CASCADE)
    interp = models.TextField(max_length=200)
    date_de_création = models.DateTimeField(auto_now_add=True)


class Utilisateur(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField("Email ", max_length=30)

    def __str__(self):
        return self.user.username




