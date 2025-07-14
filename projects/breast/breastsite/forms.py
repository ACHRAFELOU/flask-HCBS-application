from django import forms
from django.forms.widgets import NumberInput
YEARS=[x for x in range(1950,2010)]
sex =[
      ('', 'Choose....'),
      ('Femme', 'Femme'),
      ('Homme', 'Homme'),
]
quartiers=[
    ('', 'Choose....'),
    ('Riad_agdal', 'Riad_agdal'),
    ('Hassan', 'Hassan'),
    ('Alfath', 'Alfath'),
    ('Hassan', 'Hassan'),
    ('Yaakoub El Mansour', 'Yaakoub El Mansour'),

]

class RegistrationForm(forms.Form):
    first_name= forms.CharField(widget=forms.TextInput(attrs={'placeholder':'First_name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Last_name'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'email'}))
    cin = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'CIN'}))
    sex = forms.CharField(widget=forms.Select(choices= sex))
    phone = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'+212 (0) '}))
    age = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    quartier = forms.CharField(widget=forms.Select(choices= quartiers))
