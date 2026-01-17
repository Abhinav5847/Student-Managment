from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import registerForm
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def student(request):
   return render(request,'students.html')

def register_view(request):
   
   if request.method == 'POST':
      
      form = registerForm(request.POST)
      if form.is_valid():
         user = form.save(commit=False)
         user.is_active = False
         user.save()

         send_mail(
            subject='regitration successfull completed',
            message=f"hii {user.username},your account has been created successfully.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
         )

         return redirect('login')
   else:
         form = registerForm()

   return render(request,'register.html',{'form':form})   
  
def login_view(request):
   if request.method == 'POST':
      form = AuthenticationForm(request,data=request.POST)
      if form.is_valid():
         user = form.get_user()
         login(request,user)
         return redirect('student')
   else:
      form = AuthenticationForm()

   return render(request,'login.html')      
    

def logout_view(request):
   logout(request)
   return redirect('login')