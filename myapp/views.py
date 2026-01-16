from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User

def student(request):
   return render(request,'students.html')

def register_view(request):
   if request.method == 'POST':
      username = request.POST['username']
      email = request.POST['email']
      password1 = request.POST['password1']
      password2 = request.POST['password2']

      if password1 != password2:
          messages.error(request,"password doest not match")
          return redirect('register')
      
      if User.objects.filter(username=username).exists():
         messages.error(request,'username is already exit!')
         return redirect('register')

      User.objects.create_user(
         username=username,
         email=email,
         password=password1
      ) 

      messages.success(request,'registration completed')

      return render(request,'login.html')  
      


# Create your views here.
