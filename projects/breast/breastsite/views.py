from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User,auth
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
#from .forms import MedForm, PatForm, ContactForm
from .models import Contact, Image, Interprétation, Patient, Médecin, Utilisateur


def accueil(request):
    return render(request, 'base_app/accueil.html')


def inscription(request):
    if request.method == 'GET':
        dict_inscription_form = {'form': UserCreationForm()}
        return render(request, 'base_app/inscription.html', dict_inscription_form)

    if request.method == 'POST':
        form= UserCreationForm(request.POST)
        # Creer un nouveau compte
        if request.POST['password1'] == request.POST['password2']:
            if form.is_valid():
             try:
                # Enregistrer ses données
                user=form.save()
                # Se Connecter directement
                login(request, user)
                return render(request, 'base_app/apres-inscription.html')

             except IntegrityError:
                dict_form_error = {'form': UserCreationForm(), 'error': "Ce nom d'utilisateur existe déjà"}
                return render(request, 'base_app/inscription.html', dict_form_error)

        else:
            # Probléme dans le mot de passe
            dict_form_error = {'form': UserCreationForm(), 'error': 'Le mot de passe ne correspond pas'}
            return render(request, 'base_app/inscription.html', dict_form_error)


# apres Connection page
def apres_inscription(request):
    return render(request, 'base_app/apres-inscription.html')

def apres_connection_medecin(request):
    return render(request, 'base_app/apres_connection_medecin')


# deconnexion
def logout(request):
        auth.logout(request)
        return redirect('accueil')


# se connecter
def se_connecter(request) :

    if request.method == 'GET' :
        return render(request, 'base_app/connection.html', { 'form' : AuthenticationForm() })
    else :
        user = authenticate(request, username=request.POST['username'], password = request.POST['password'])
        if user is None :
            return render(request,'base_app/inscription.html', {'form' : UserCreationForm(), 'error' : "Le nom d'utilisateur ou le mot de passe ne correspond pas"})
        else :
            login(request, user)
            return render(request, 'base_app/se_connecter.html')


def Medformpage(request):
    form = MedForm(request.POST)
    username = request.user
    context = {
        "form": MedForm
    }
    if request.method == 'GET':
      return render(request, 'base_app/inscription-finale-medecin.html', context)

    elif form.is_valid() :
        newforms = Médecin(
                          username=request.user,
                          nom=form.cleaned_data['nom'],
                          prénom=form.cleaned_data['prénom'],
                          cin=form.cleaned_data['cin'],
                          date_de_naissance=form.cleaned_data['date_de_naissance'],
                          sexe=form.cleaned_data['sexe'],
                          quartier=form.cleaned_data['quartier'],
                          spécialité=form.cleaned_data['spécialité'])


        new_user=form.save(commit=False)
        new_user.username.request.user
        new_user.save()
        return redirect('accueil')




def Patformpage(request):
    form = PatForm(request.POST)
    context = {
        "form": PatForm
    }
    if request.method == 'GET':
     return render(request, 'base_app/inscription-finale-patient.html', context)


    elif form.is_valid() :

          newform= Patient(
                         username = User,
                         nom=form.cleaned_data['nom'],
                         prénom=form.cleaned_data['prénom'],
                         cin=form.cleaned_data['cin'],
                         date_de_naissance=form.cleaned_data['date_de_naissance'],
                         sexe=form.cleaned_data['sexe'],
                         quartier=form.cleaned_data['quartier'])

          newform.user = request.user
          newform.save()

    return redirect('accueil')

def connection(request):
    return render(request, 'base_app/connection.html',{ 'form' : AuthenticationForm() })