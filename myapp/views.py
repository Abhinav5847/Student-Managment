from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import registerForm
from django.http import HttpResponse
from django.conf import settings
from .decorators import student_required

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

         current_site = get_current_site(request)
         uid = urlsafe_base64_encode(force_bytes(user.pk))
         token = default_token_generator.make_token(user)

         activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

         email = EmailMessage(
            'Activate your acccount',
            f"""
            Hi {user.username},

Click the link below to activate your account:

{activation_link}

If you did not register, ignore this email.
                """,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
         )
         email.send()

         return HttpResponse("Registration successful. Check your email to activate your account.")
   else:
         form = registerForm()

   return render(request,'register.html',{'form':form})   


def activate_account(request,uidb64,token):
   try:
      uid = force_str(urlsafe_base64_decode(uidb64))
      user = User.objects.get(pk=uid)
   except(TypeError,ValueError,User.DoesNotExist):
      user = None

   if user and default_token_generator.check_token(user,token):
      user.is_active = True
      user.save()
      return redirect('login')
   else:
      return HttpResponse("Activation link is invalid or expired.")      




  
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

        if not user.is_active:
            return render(request, 'login.html', {
                'error': 'Account not activated. Check your email.'
            })

        login(request, user)
        return redirect('student')

    return render(request, 'login.html')     
    

def logout_view(request):
   if request.method == "POST":
      logout(request)
      return redirect('login')
   
@student_required
def student_profile(request):
   profile = student   