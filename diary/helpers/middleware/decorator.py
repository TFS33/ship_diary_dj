from django.utils import translation
from django.conf import settings
from functools import wraps


def activate_user_language(request):
    user_language = request.COOKIES.get("django_language", settings.LANGUAGE_CODE)
    translation.activate(user_language)
    request.session["django_language"] = user_language
    return translation.get_language()


def with_user_language(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        current_language = activate_user_language(request)
        response = view_func(request, *args, **kwargs)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, current_language)
        return response

    return wrapper
