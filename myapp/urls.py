from django.urls import path
from . import views

urlpatterns = [
    path("students/",views.student,name='student'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout')
]