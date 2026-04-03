from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def accountant_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        if request.user.role != 'ACCOUNTANT':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
