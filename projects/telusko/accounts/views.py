from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None :
            auth.login(request,user)
            return redirect("/")
        else :
            messages.info(request,'invalid credentials')
            return redirect('login')
    else:
        return render(request,'logino.html')


def Inscription_Patient(request):
    if request.method =='POST':
        first_name =request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        cin = request.POST['cin']
        sexe = request.POST['sexe']
        date_naissance = request.POST['date_naissance']
        quartier = request.POST['quartier']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user = User.objects.create_user(username = username,password=password1,email=email,cin=cin,sexe=sexe,date_naissance=date_naissance,quartier=quartier,first_name=first_name,last_name=last_name)
        user.save();
        print('user created')
        return redirect('/')
    else:
        return render(request,'Inscription_Patient.html')