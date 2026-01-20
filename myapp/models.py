from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin','Admin'),
        ('student','Student')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
#userpage    

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )  
    roll_number = models.CharField(max_length=20,unique=True,blank=True,null=True)
    department =  models.CharField(max_length=100,blank=True,null=True)
    year_of_admission = models.PositiveIntegerField(blank=True,null=True)
    date_of_birth = models.DateField(blank=True,null=True)
    profile_picture = models.ImageField(upload_to='profile_picture',null=True,blank=True)

    def save(self,*args,**kwargs):
        if not self.roll_number:
            last_student = StudentProfile.objects.order_by('-id').first()
            if last_student and last_student.roll_number and last_student.roll_number.isdigit():
                self.roll_number = str(int(last_student.roll_number)+1)
            else:
                self.roll_number = '1'
        super().save(*args,**kwargs)        

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"     
    
    
