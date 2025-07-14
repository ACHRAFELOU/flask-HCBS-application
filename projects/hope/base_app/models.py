from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver

specialite_types = [
    ('', 'Choose....'),
    ('Aucune','Aucune'),
    ('chirurgien','chirurgien'),
    ('Cancérologue','Cancérologue'),
    ('Gynécologue','Gynécologue')
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
class Utilisateur(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField("Email ", max_length=30)

    def __str__(self):
        return self.user.username

class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,)
    nom = models.CharField("Nom ",max_length=30)
    prenom = models.CharField("Prenom ", max_length=30)
    cin = models.CharField("C.I.N ", max_length=10)
    date_de_naissance = models.DateField(null=True, blank=True)
    specialite = models.CharField(max_length=20, choices=specialite_types, default='spa')
    sexe = models.CharField(max_length=10, choices=sex_types, default='1')
    quartier = models.CharField(max_length=20, choices=quartier_types, default='0')
    picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.prénom + ' ' + self.nom

class Patient(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True,)
    nom = models.CharField("Nom ",max_length=30)
    prenom = models.CharField("Prenom ", max_length=30)
    cin = models.CharField("C.I.N ", max_length=10)
    date_de_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=10, choices=sex_types, default='1')
    quartier = models.CharField(max_length=20, choices=quartier_types, default='0')
    picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.prenom + ' ' + self.nom


class Contact(models.Model):
    nom = models.CharField("Nom", max_length=30)
    prenom = models.CharField("Prenom ", max_length=30)
    email = models.EmailField("Email ", max_length=30)
    password = models.CharField("password ", max_length=30)
    message = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.prenom + ' ' + self.nom

class Contact_medecin(models.Model):
    nom = models.CharField("Nom", max_length=30)
    prenom = models.CharField("Prenom ", max_length=30)
    email = models.EmailField("Email ", max_length=30)
    password = models.CharField("password ", max_length=30)
    message = models.CharField(max_length=200, blank=True)

class Consultation(models.Model):
    id_patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_de_consultation = models.DateTimeField(auto_now_add=True)
    def __int__(self):
        return (self.id,self.date_de_consultation)

class Image_data(models.Model):
    id_patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    id_consultation  = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    Data_img = models.CharField(max_length=1000)
    date_de_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.Data_img


class Interpretation(models.Model):
    id_medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    id_consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date_de_interpretation = models.DateTimeField(auto_now_add=True)
    commentaire = models.CharField(max_length=2000, blank=True)
    def __str__(self):
        return self.id_medecin



