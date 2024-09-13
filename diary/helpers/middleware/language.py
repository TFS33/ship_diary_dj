from django.utils import translation
from django.conf import settings
from django.urls import resolve, Resolver404


class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            url_language = resolve(request.path_info).kwargs.get('language')
        except Resolver404:
            url_language = None

        if url_language:
            # Language specified in the URL takes precedence
            language = url_language
        elif request.user.is_authenticated and hasattr(request.user, 'user_set_language'):
            # Use authenticated user's preference if available
            language = request.user.user_set_language or settings.LANGUAGE_CODE
        else:
            # Fall back to cookie or default language
            language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, settings.LANGUAGE_CODE)

        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        # Set language cookie if it has changed
        if 'Content-Language' not in response:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

        return response
