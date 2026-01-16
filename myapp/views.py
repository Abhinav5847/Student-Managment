from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required

def student(request):
   return render(request,'students.html')

def register_view(request):
   if request.method == 'POST':
      username = request.POST.get('username')
      email = request.POST.get('email')
      password1 = request.POST.get('password1')
      password2 = request.POST.get('password2')

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
      return redirect('login')

   return render(request,'register.html')
  

def login_view(request):
   if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')

      user = authenticate(request,username=username,password=password)

      if user:
         login(request,user)
         return redirect('student')
      else:
         messages.error(request,'Invalid credentials')

   return render(request,'login.html')      

def logout_view(request):
   

      


