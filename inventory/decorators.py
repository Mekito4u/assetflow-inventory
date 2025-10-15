from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import UserProfile


def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.role not in allowed_roles:
                    return HttpResponseForbidden("Недостаточно прав")
            except UserProfile.DoesNotExist:
                user_profile = UserProfile.objects.create(
                    user=request.user,
                    role='employee'
                )
                if user_profile.role not in allowed_roles:
                    return HttpResponseForbidden("Недостаточно прав")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator