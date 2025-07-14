from django.forms import ModelForm
from django import forms
from django.forms.widgets import NumberInput
from .models import Medecin, Patient, Contact, Utilisateur, Image_data ,Interpretation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import models

YEARS=[x for x in range(1950,2010)]
sexe =[
      ('', 'Choose....'),
      ('Femme', 'Femme'),
      ('Homme', 'Homme'),
]
quartiers=[
    ('', 'Choose....'),
    ('Riad_agdal', 'Riad_agdal'),
    ('Agdal', 'Agdal'),
    ('Alfath', 'Alfath'),
    ('Hassan', 'Hassan'),
    ('Yaakoub El Mansour', 'Yaakoub El Mansour'),

]
specialite_types = [
    ('', 'Choose....'),
    ('Aucune','Aucune'),
    ('chirurgien','chirurgien'),
    ('Cancérologue','Cancérologue'),
    ('Gynécologue','Gynécologue')
]
# class UserForm(ModelForm):

# class Meta():
# model = Utilisateur


class MedForm(forms.Form):
    nom= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First_name'}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last_name'}))
    cin = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'CIN'}))
    #image_Identite = forms.ImageField()
    sexe = forms.CharField(widget=forms.Select(choices= sexe))
    date_de_naissance = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    quartier = forms.CharField(widget=forms.Select(choices= quartiers))
    specialite = forms.CharField(widget=forms.Select(choices= specialite_types))
    picture=forms.ImageField()

# class ImageUploadForm(forms.Form):
#     profile_photo = forms.ImageField()

class PatForm(forms.Form):
    nom= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First_name'}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last_name'}))
    cin = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'CIN'}))
    sexe = forms.CharField(widget=forms.Select(choices= sexe))
    date_de_naissance = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    quartier = forms.CharField(widget=forms.Select(choices= quartiers))
    picture = forms.ImageField()


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Utilisateur
        fields = ['user', 'email']


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'message']


class CommentaireForm(forms.Form):
    commentaire= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'commentaire'}))





