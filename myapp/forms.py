from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from .models import StudentProfile
from django.contrib.auth import get_user_model

user = get_user_model()

class registerForm(UserCreationForm):
    email = forms.EmailField(required=True)
    education = forms.CharField(required=True)
    year_of_admission = forms.IntegerField(required=True)
    date_of_birth = forms.DateField(required=True)
    profile_picture = forms.ImageField(required=False)


    class Meta:
        model = User
        fields = ['username','email','password1','password2','education','year_of_admission','date_of_birth','profile_picture']

    def save(self,commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save() 

            profile,created = StudentProfile.objects.get_or_create(user=user)
            profile.education = self.cleaned_data['education']
            profile.year_of_admission = self.cleaned_data['year_of_admission']
            profile.date_of_birth = self.cleaned_data['date_of_birth']

            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            profile.save()

        return user        