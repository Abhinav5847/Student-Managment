from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import registerForm
from django.http import HttpResponse
from django.conf import settings
from .decorators import student_required
from .decorators import admin_required
from .models import StudentProfile
from django.contrib import messages
from .models import Course
from django.views.decorators.cache import never_cache

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

User = get_user_model()

@never_cache
@login_required
@admin_required
def admin_dashboard(request):
    students = User.objects.filter(role='student').select_related('student_profile')
    return render(request,'admin_dashboard.html',{'students':students})

@never_cache
@login_required
@admin_required
def admin_student_edit(request,student_id):
    student = get_object_or_404(User,pk=student_id,role='student')
    profile,_ = StudentProfile.objects.get_or_create(user=student)

    if request.method == "POST":
        student.username = request.POST.get('username')
        student.email = request.POST.get('email')
        student.save()

        profile.department = request.POST.get('department',profile.department)
        profile.year_of_admission = request.POST.get('year_of_admission',profile.year_of_admission)
        profile.date_of_birth = request.POST.get('date_of_birth',profile.date_of_birth)
        profile.profile_picture = request.POST.get('profile_picture',profile.profile_picture)
        profile.save()
        return redirect('admin_dashboard')
    
    return render(request,'edit_student.html',{'student':student,'profile':profile})

@never_cache
@login_required
@admin_required
def admin_student_delete(request,student_id):
    student = get_object_or_404(User,pk=student_id,role='student')
    student.delete()
    return redirect('admin_dashboard')

@never_cache
@login_required
@admin_required
def create_course(request):
    if request.method == 'POST':
        Course.objects.create(
            title=request.POST.get('title'),
            description = request.POST.get('description'),
            price = request.POST.get('price')
        )
        return redirect('admin_course_list')
    
    return render(request,'create_course.html')

@never_cache
@login_required
@admin_required
def admin_course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request,'admin_course_list.html',{'courses':courses})

@never_cache
@login_required
@admin_required
def admin_course_edit(request,course_id):
    course = get_object_or_404(Course,id=course_id)

    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.price = request.POST.get('price')
        course.save()

        messages.success(request,"course edited successfully")
        return redirect('admin_course_list')

    return render(request,'admin_edit_course.html',{'course':course})
 
@never_cache
@login_required
@admin_required
def admin_course_delete(request,course_id):
    course =get_object_or_404(Course,id=course_id)
    course.delete()
    messages.success(request,"course deleted")
    return redirect('admin_course_list')

@never_cache
@login_required
@admin_required
def course_status(request,course_id):
    course = get_object_or_404(Course,id=course_id)
    course.is_active = not course.is_active
    course.save()

    status = "activated" if course.is_active else "deactived"
    messages.success(request,f"Course {status} success")
    return redirect('admin_course_list')

   



@never_cache
@login_required
@student_required
def student_dashboard(request):
    profile,created =StudentProfile.objects.get_or_create(user=request.user)
    return render(request,'students_dashboard.html',{'profile':profile})

@login_required
@student_required
@never_cache
def student_profile_edit(request):
    profile,_ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.email = request.POST.get('email')
        request.user.save()

        profile.department = request.POST.get('department')
        profile.year_of_admission = request.POST.get('year_of_admission')

        date_of_birth = request.POST.get('data_of_birth')
        if date_of_birth:
         profile.date_of_birth = request.POST.get('date_of_birth')

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']


        profile.save()

        return redirect('student_dashboard')
    
    return render(request,'students_profileedit.html',{'profile':profile}) 

@never_cache
@login_required
@student_required
def student(request):
    return render(request, 'students.html')


def register_view(request):
    if request.method == 'POST':
        form = registerForm(request.POST,request.FILES)
        if form.is_valid():
    
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile_picture = form.cleaned_data.get('profile_picture')

            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': form.cleaned_data['department'],
                    'year_of_admission': form.cleaned_data['year_of_admission'],
                    'date_of_birth': form.cleaned_data['date_of_birth'],
                    'profile_picture':profile_picture
                }
            )
   
            if not created:
                profile.department = form.cleaned_data['department']
                profile.year_of_admission = form.cleaned_data['year_of_admission']
                profile.date_of_birth = form.cleaned_data['date_of_birth']
                if profile_picture:
                    profile.profile_picture = profile_picture
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
        
        if user:
         login(request, user)
         messages.success(request,"LOGIN SUCCESS !")
         return redirect('home')
        else:
            messages.error(request,"Invalid username or password")

    return render(request, 'login.html')


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request,"logout")
        return redirect('login')


@student_required
@login_required
def student_profile(request):
  
    if request.user.role != 'student':
        return redirect('login')

  
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    return render(request, 'userprofile.html', {'profile': profile})
