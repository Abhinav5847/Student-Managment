from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import registerForm
from django.http import HttpResponse
from django.conf import settings
from .decorators import student_required
from .decorators import admin_required
from .models import StudentProfile

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

User = get_user_model()


@login_required
@admin_required
def admin_dashboard(request):
    students = User.objects.filter(role='student').select_related('student_profile')
    return render(request,'admin_dashboard.html',{'students':students})


def student(request):
    return render(request, 'students.html')


def register_view(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
    
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': form.cleaned_data['department'],
                    'year_of_admission': form.cleaned_data['year_of_admission']
                }
            )
   
            if not created:
                profile.department = form.cleaned_data['department']
                profile.year_of_admission = form.cleaned_data['year_of_admission']
                profile.save()

      
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            email = EmailMessage(
                'Activate your account',
                f"Hi {user.username},\n\nClick the link below to activate your account:\n\n{activation_link}\n\nIf you did not register, ignore this email.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            email.send()

            return HttpResponse("Registration successful. Check your email to activate your account.")
    else:
        form = registerForm()

    return render(request, 'register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
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
            return render(request, 'login.html', {'error': 'Invalid username or password'})

        if not user.is_active:
            return render(request, 'login.html', {'error': 'Account not activated. Check your email.'})

        login(request, user)
        return redirect('student')

    return render(request, 'login.html')


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')


@student_required
@login_required
def student_profile(request):
  
    if request.user.role != 'student':
        return redirect('login')

  
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    return render(request, 'userprofile.html', {'profile': profile})
