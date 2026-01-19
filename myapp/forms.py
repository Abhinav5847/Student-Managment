from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from .models import StudentProfile
from django.contrib.auth import get_user_model

user = get_user_model()

class registerForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.CharField(required=True)
    year_of_admission = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username','email','password1','password2','department','year_of_admission']

    def save(self,commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save() 

            profile,created = StudentProfile.objects.get_or_create(user=user)
            profile.department = self.cleaned_data['department']
            profile.year_of_admission = self.cleaned_data['year_of_admission']
            profile.save()

            # StudentProfile.objects.create(
            #     user=user,
            #     department=self.cleaned_data['department'],
            #     year_of_admission=self.cleaned_data['year_of_admission']
            # )

        return user        