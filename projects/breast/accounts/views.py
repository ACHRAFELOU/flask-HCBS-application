from django.shortcuts import render,redirect
from django.contrib.auth.models import User , auth
from django.contrib import messages
# Create your views here.
def registre(request):

    if request.method == 'POST':
        first_name= request.POST['first_name']
        last_name  = request.POST['last_name']
        username  = request.POST['username']
        password = request.POST['password']
        email  = request.POST['email']


        user= User.objects.create_user(first_name=first_name,last_name=last_name,password=password,username=username,email=email)
        user.save();
        messages.add_message(request, messages.SUCCESS,"you have signup successfully")
        return redirect('registre')
    else:
        return render(request,'registre.html')