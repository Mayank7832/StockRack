from functools import wraps
from django.shortcuts import redirect

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.myuser:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view