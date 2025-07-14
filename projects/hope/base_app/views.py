from datetime import datetime
import serial
from PIL import Image

import random
import serial, time
import csv
import pyautogui
import pyscreeze
import matplotlib as plt
import numpy as np
import cv2
from .forms import UserRegisterForm
from django.core import serializers
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, auth
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import MedForm, PatForm, ContactForm,CommentaireForm
from .models import Contact , Patient, Medecin, Utilisateur,Image_data, Interpretation,Consultation
from .models import *

import numpy as np
import cv2
import serial, time
import csv
import pyautogui
import pyscreeze
import matplotlib as plt

import base64
from io import BytesIO
from .filters import OrderFilter

n = 225
pix = [[0] * n for p in range (n)]
r = [[0] * n for p in range (n)]
g = [[0] * n for p in range (n)]
b = [[0] * n for p in range (n)]

m = 8
Name = [[0] * n for p in range (m)]

minimum = 10
maximum = 22

RealPix = 12

levelGrad1 = 1.5
levelGrad2 = 2.0
levelGrad3 = 2.5

img = np.zeros((180,180,3), np.uint8)
img[:] = (255, 255, 255)

# from .forms import ImageUploadForm


def to_image(numpy_img):
    img = Image.fromarray(numpy_img, 'RGB')
    return img

def to_data_uri(pil_img):
    data = BytesIO()
    pil_img.save(data, "JPEG") # pick your format
    data64 = base64.b64encode(data.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')

def accueil(request):
    return render(request, 'base_app/accueil.html')


def inscription(request):
    global global_id_user
    if request.method == 'GET':
        dict_inscription_form = {'form': UserCreationForm()}
        return render(request, 'base_app/inscription.html', dict_inscription_form)

    else:
        # Creer un nouveau compte
        if request.POST['password1'] == request.POST['password2']:

            try:
                # Enregistrer ses données
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])

                user.save()
                request.session['id_achraf'] = user.id
                global_id_user = request.session['id_achraf']
                print(global_id_user)
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

def Connection_Patient(request):
    return render(request, 'base_app/apres_connection_patient.html')


def Connection_Doctor(request):
    return render(request, 'base_app/Page_doctor.html')

def Connection_historique(request,global_id_user):

    patient = Patient.objects.get(user_id=global_id_user)
    images = patient.consultation_set.all()
    imag_data = patient.image_data_set.all()
    data=OrderFilter(request.GET,queryset=imag_data)
    imag_data=data.qs
    #data = Patient.objects.raw('SELECT * FROM base_app_image_data as data where data.id_consultation_id = %s', [imag_data[32].id_consultation_id])
    #test=data.objects.filter(imag_data=imag_data)

    print('................................................',data)
    print('................................................', imag_data)
    context ={'patient' : patient,'images' : images, 'imag_data' : imag_data ,'data' : data}
    return render(request, 'base_app/historique_patient.html',context)

def Calender_date(request):
    return render(request, 'base_app/calender.html')
    return render(request, 'base_app/calender.html')
# def apres_connection_medecin(request):
#     return render(request, 'base_app/apres_connection_medecin')


# deconnexion
def logout(request):
    auth.logout(request)
    return redirect('accueil')

# se connecter
def se_connecter(request):
    global global_id_user
    if request.method == 'GET':
        return render(request, 'base_app/connection.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'base_app/inscription.html', {'form': UserCreationForm(),
                                                                 'error': "Le nom d'utilisateur ou le mot de passe ne correspond pas"})
        else:
            login(request, user)
            request.session['id_achraf_conct'] = user.id
            global_id_user = user.id

            st = Patient.objects.filter(user=user.id)
            print(len(st))
        if len(st) == 0:
            st = Medecin.objects.filter(user=user.id)
            print(len(st))
            if len(st) == 0:
                return render(request, 'base_app/apres-inscription.html', {'st': st})
            else:
                p = Patient.objects.raw('SELECT p.* FROM base_app_patient as p where p.quartier = %s', [st[0].quartier])
                # for x in p:
                #     print(x)
                return render(request, 'base_app/Page_doctor.html', {'p': p})
        else:
            return render(request, 'base_app/apres_connection_patient.html', {'st': st})

def Medformpage(request):
    form = MedForm(request.POST,request.FILES)
    context = {
        "form": MedForm,
    }
    if request.method == 'GET':
        return render(request, 'base_app/inscription-finale-medecin.html', context)

    if form.is_valid():
        newforms = Medecin(
            user=User.objects.get(id=global_id_user),
            nom=form.cleaned_data['nom'],
            prenom=form.cleaned_data['prenom'],
            cin=form.cleaned_data['cin'],
            date_de_naissance=form.cleaned_data['date_de_naissance'],
            sexe=form.cleaned_data['sexe'],
            quartier=form.cleaned_data['quartier'],
            specialite=form.cleaned_data['specialite'],
            picture=form.cleaned_data['picture'])
        newforms.save()
        # if 'picture' in request.FILES:
        #     newforms.picture = request.FILES['picture']
        #
        # else:
        #    print(newforms.errors, newforms.errors)

    return redirect('accueil')

def Patformpage(request):
    form = PatForm(request.POST,request.FILES)
    # photo_upload_form = ImageUploadForm(request.POST, request.FILES)
    context = {
        "form": PatForm,
        # "photo_upload_form": photo_upload_form
    }
    if request.method == 'GET':
        return render(request, 'base_app/inscription-finale-patient.html', context)

    if form.is_valid():
        newform = Patient(
            user=User.objects.get(id=global_id_user),
            nom=form.cleaned_data['nom'],
            prenom=form.cleaned_data['prenom'],
            cin=form.cleaned_data['cin'],
            date_de_naissance=form.cleaned_data['date_de_naissance'],
            sexe=form.cleaned_data['sexe'],
            quartier=form.cleaned_data['quartier'],
            picture=form.cleaned_data['picture'])

        newform.save()
    # if photo_upload_form.is_valid():
    #           user = newform.user
    #           avatar = photo_upload_form.cleaned_data.get("profile_photo")
    #           new_user_profile = Patient.objects.create(user, avatar)
    #           new_user_profile.save()
    return redirect('accueil')

def connection(request):
    return render(request, 'base_app/connection.html', {'form': AuthenticationForm()})

def fetch_sensor_values_ajax(request):
    data = {}
    if request.is_ajax():
        com_port_s = request.GET.get('id', None)
        # sensor_val=random.random() # auto random value if sendor is not connected , you can remove this line
        sensor_val = []
        sensors = 9
        sensor_data = []
        now = datetime.now()
        ok_date = str(now.strftime('%Y-%m-%d %H:%M:%S'))
        try:
            # sr=serial.Serial("COM9",9600)
            sr = serial.Serial(com_port_s, 115200)
            for i in range(0, 4, 1):
                st = list(str(sr.readline(), 'utf-8'))

            sr.close()
            sensor_val = str(''.join(st[:]))
            print("sensor_val :;:::::::::::::::::::::::::::  ", sensor_val[0]);
            for s in range(0, sensors):
                if (sensor_val):
                    sensor_data[s].append(str(sensor_val[s]) + ',' + ok_date)
                    print("sensor_data :;:::::::::::::::::::::::::::  ", sensor_data[0]);
                else:
                    sensor_data[s].append(str(sensor_val[s]) + ',' + ok_date)
        except Exception as e:
            print(e)
            sensor_data.append(str(sensor_val) + ',' + ok_date)
            Image_Patient(sensor_data)
        data['result'] = sensor_data

    else:
        data['result'] = 'Not Ajax'
    return JsonResponse(data)

def fetch_saved_sensor_values_ajax(request):
    data = {}

    patient = Patient.objects.get(user_id=global_id_user)
    imag_data = patient.image_data_set.all()
    filtered_data=OrderFilter(request.GET,queryset=imag_data)
    imag_data=filtered_data.qs
    #data = Patient.objects.raw('SELECT * FROM base_app_image_data as data where data.id_consultation_id = %s', [imag_data[32].id_consultation_id])
    #test=data.objects.filter(imag_data=imag_data)

    print('................................................',filtered_data)
    print('................................................', imag_data)
    qs_json = serializers.serialize('json', imag_data)

    data['result'] = qs_json
    return JsonResponse(data,safe=False)


def show_graph(request):
    return render(request, 'base_app/live_graph.html')

def DoctorProfile(request):
    return render(request, 'base_app/Doctor_profile.html')

def rgb(minimum, maximum, value):
    if value > maximum:
        value = maximum

    if value < minimum:
        value = minimum

    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return b1, g1, r1

def grad1(level, PixelTemperature, x1, y1):
    PixelTemperature = PixelTemperature - level
    (rg, gg, bg) = rgb(minimum, maximum, PixelTemperature)

    for y in range(y1 - RealPix, y1 - RealPix + 3 * RealPix, RealPix):
        for x in range(x1 - RealPix, x1 - RealPix + 3 * RealPix, RealPix):
            if (x == x1 and y == y1):
                continue
            else:
                cv2.rectangle(img, (x, y), (x + RealPix, y + RealPix), (bg, gg, rg), -1)

def grad2(level, PixelTemperature, x1, y1):
    PixelTemperature = PixelTemperature - level
    (rg, gg, bg) = rgb(minimum, maximum, PixelTemperature)

    for y in range(y1 - 2 * RealPix, y1 - 2 * RealPix + 5 * RealPix, RealPix):
        for x in range(x1 - 2 * RealPix, x1 - 2 * RealPix + 5 * RealPix, RealPix):
            cv2.rectangle(img, (x, y), (x + RealPix, y + RealPix), (bg, gg, rg), -1)

def grad3(level, PixelTemperature, x1, y1):
    PixelTemperature = PixelTemperature - level
    (rg, gg, bg) = rgb(minimum, maximum, PixelTemperature)

    for y in range(y1 - 3 * RealPix, y1 - 3 * RealPix + 7 * RealPix, RealPix):
        for x in range(x1 - 3 * RealPix, x1 - 3 * RealPix + 7 * RealPix, RealPix):
            cv2.rectangle(img, (x, y), (x + RealPix, y + RealPix), (bg, gg, rg), -1)

def fetch_termal_image_ajax(request):
    data = {}
    if request.is_ajax():
        com_port = request.GET.get('id', None)
        sr = serial.Serial(com_port, 115200)

        for i in range(0, 4, 1):
            serial_line = sr.readline()

        sr.close()

        liste = serial_line.split(','.encode())
        liste[-1] = liste[-1].strip()
        # Image_Patient(liste)
        pix[0] = float(liste[0])
        pix[7] = float(liste[1])
        pix[14] = float(liste[2])
        pix[105] = float(liste[3])
        pix[112] = float(liste[4])
        pix[119] = float(liste[5])
        pix[210] = float(liste[6])
        pix[217] = float(liste[7])
        pix[224] = float(liste[8])

        (r[0], g[0], b[0]) = rgb(minimum, maximum, pix[0])
        (r[7], g[7], b[7]) = rgb(minimum, maximum, pix[7])
        (r[14], g[14], b[14]) = rgb(minimum, maximum, pix[14])
        (r[105], g[105], b[105]) = rgb(minimum, maximum, pix[105])
        (r[112], g[112], b[112]) = rgb(minimum, maximum, pix[112])
        (r[119], g[119], b[119]) = rgb(minimum, maximum, pix[119])
        (r[210], g[210], b[210]) = rgb(minimum, maximum, pix[210])
        (r[217], g[217], b[217]) = rgb(minimum, maximum, pix[217])
        (r[224], g[224], b[224]) = rgb(minimum, maximum, pix[224])

        grad3(levelGrad3, pix[0], 0, 0)
        grad3(levelGrad3, pix[7], 84, 0)
        grad3(levelGrad3, pix[14], 168, 0)
        grad3(levelGrad3, pix[105], 0, 84)
        grad3(levelGrad3, pix[112], 84, 84)
        grad3(levelGrad3, pix[119], 168, 84)
        grad3(levelGrad3, pix[210], 0, 168)
        grad3(levelGrad3, pix[217], 84, 168)
        grad3(levelGrad3, pix[224], 168, 168)

        grad2(levelGrad2, pix[0], 0, 0)
        grad2(levelGrad2, pix[7], 84, 0)
        grad2(levelGrad2, pix[14], 168, 0)
        grad2(levelGrad2, pix[105], 0, 84)
        grad2(levelGrad2, pix[112], 84, 84)
        grad2(levelGrad2, pix[119], 168, 84)
        grad2(levelGrad2, pix[210], 0, 168)
        grad2(levelGrad2, pix[217], 84, 168)
        grad2(levelGrad2, pix[224], 168, 168)

        cv2.rectangle(img, (0, 0), (12, 12), (b[0], g[0], r[0]), -1)
        cv2.rectangle(img, (84, 0), (96, 12), (b[7], g[7], r[7]), -1)
        cv2.rectangle(img, (168, 0), (180, 12), (b[14], g[14], r[14]), -1)
        cv2.rectangle(img, (0, 84), (12, 96), (b[105], g[105], r[105]), -1)
        cv2.rectangle(img, (84, 84), (96, 96), (b[112], g[112], r[112]), -1)
        cv2.rectangle(img, (168, 84), (180, 96), (b[119], g[119], r[119]), -1)
        cv2.rectangle(img, (0, 168), (12, 180), (b[210], g[210], r[210]), -1)
        cv2.rectangle(img, (84, 168), (96, 180), (b[217], g[217], r[217]), -1)
        cv2.rectangle(img, (168, 168), (180, 180), (b[224], g[224], r[224]), -1)

        grad1(levelGrad1, pix[0], 0, 0)
        grad1(levelGrad1, pix[7], 84, 0)
        grad1(levelGrad1, pix[14], 168, 0)
        grad1(levelGrad1, pix[105], 0, 84)
        grad1(levelGrad1, pix[112], 84, 84)
        grad1(levelGrad1, pix[119], 168, 84)
        grad1(levelGrad1, pix[210], 0, 168)
        grad1(levelGrad1, pix[217], 84, 168)
        grad1(levelGrad1, pix[224], 168, 168)

        bicubic_img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        pil_image = to_image(bicubic_img)
        image_uri = to_data_uri(pil_image)

        data['result'] = image_uri
        return JsonResponse(data)

def show_thermal(request):
    return render(request, 'base_app/thermal_live_Data.html')

def create_Consultation(self):
    global global_id_consultation
    newConsultation = Consultation(
        id_patient=Patient.objects.get(user_id=global_id_user))
    newConsultation.save()
    global_id_consultation = newConsultation.id

def Image_Patient(data):
    global global_id_consultation
    newImage_data = Image_data(
        id_patient=Patient.objects.get(user_id=global_id_user),
        Data_img = str(data),
        id_consultation = Consultation.objects.get(id=global_id_consultation))
    newImage_data.save()


def Consultation_patient(request):
    return render(request, 'base_app/Consultation.html')

def Interpretformpage(request):
    form = CommentaireForm(request.POST)
    # photo_upload_form = ImageUploadForm(request.POST, request.FILES)
    context = {
        "form": CommentaireForm,
        # "photo_upload_form": photo_upload_form
    }

    if form.is_valid():
        news_form = Interpretation(
            id_medecin=User.objects.get(id=global_id_user),
            id_consultation=form.cleaned_data['id_consultation'],
            date_de_interpretation=form.cleaned_data['date_de_interpretation'],
            commentaire=form.cleaned_data['commentaire'])

        news_form.save()
    # if photo_upload_form.is_valid():
    #           user = newform.user
    #           avatar = photo_upload_form.cleaned_data.get("profile_photo")
    #           new_user_profile = Patient.objects.create(user, avatar)
    #           new_user_profile.save()
    return redirect('Connection_Doctor')
