from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #admin 
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('student/<int:student_id>/edit/',views.admin_student_edit,name='admin_student_edit'),
    path('student/<int:student_id>/delete/',views.admin_student_delete,name='admin_student_delete'),

    #student
    path('student_dashboard/',views.student_dashboard,name='student_dashboard'),
    path('student/profile/edit/',views.student_profile_edit,name='student_profile_edit'),

    path("",views.student,name='home'),
    path('login/',views.login_view,name='login'),
    path('register/',views.register_view,name='register'),
    path('activate/<uidb64>/<token>/',views.activate_account,name='active'),
    path('logout/',views.logout_view,name='logout'),
    path('user_profile/',views.student_profile,name='student_profile')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
