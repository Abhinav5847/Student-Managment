from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def student_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request,*args,**kwargs):
        if request.user.role != 'student':
            return HttpResponseForbidden("students only")
        return view_func(request,*args,**kwargs)
    return wrapper

def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request,*args,**kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden("admins only")
        return view_func(request,*args,**kwargs)
    return wrapper