from __future__ import print_function
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.conf import settings
from google.auth.exceptions import RefreshError

from .forms import (
    CustomUserForm,
    LogEntryForm,
    ShipForm,
    EngineLogForm,
    FuelLogForm,
    MaintenanceLogForm,
    NavigationLogForm,
    WeatherLogForm,
    CrewLogForm,
    LoginForm
)
from django.core.mail import send_mail

from .models import CustomUser, LogEntry, Ship
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.urls import translate_url, reverse
import logging
from django.utils.translation import gettext as _
from .helpers.middleware.decorator import with_user_language

import calendar
from calendar import HTMLCalendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

from django.core.cache import cache
import requests
from diary.helpers.credentials.weather_api import WEATHER_API_KEY
from diary.helpers.credentials.geolocation_key import ABSTRACT_GEO_KEY
import json
import weatherapi
from weatherapi.rest import ApiException
from pprint import pprint

logger = logging.getLogger(__name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # for HTTP


@with_user_language
def index(request):
    return render(request, "diary/index.html", )


@with_user_language
def register(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data["password"])
            user.save()
            login(request, user)

            send_mail(
                "Hello",
                "Hello, this is a test email",
                "LsY2T@example.com",
                ["LsY2T@example.com"],
                fail_silently=False,
            )

            return redirect("diary:user_home")
    else:
        form = CustomUserForm()
    return render(request, "diary/register.html", {"form": form, })


@login_required
@with_user_language
def user_home(request):
    user = get_object_or_404(CustomUser, pk=request.user.id)

    return render(request, "diary/user_home.html", {"user": user, })


@login_required
@with_user_language
def log_out(request):
    logout(request)
    return redirect("diary:index")


@with_user_language
def log_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("diary:user_home")
            else:
                form.add_error(str, "ups")

    else:
        form = LoginForm()

        return render(request, "diary/login.html", {"form": form})


@login_required
@with_user_language
def records(request):
    records_data = LogEntry.objects.filter(created_by=request.user).order_by("created_at")
    return render(request, "diary/records.html", {"records_data": records_data})


@login_required
@with_user_language
def ship(request):
    ship_data = Ship.objects.filter(owner=request.user).order_by("created_at")

    return render(request, "diary/ship.html", {"ship_data": ship_data})


@login_required
@with_user_language
def set_language(request):
    language = request.POST.get('language', settings.LANGUAGE_CODE)
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect(reverse('diary:user_home'))


@login_required
@with_user_language
def add_ship(request):
    if request.method == "POST":
        form = ShipForm(request.POST)
        if form.is_valid():
            ship = form.save(commit=False)
            ship.owner = request.user
            ship.save()
            return redirect("diary:ship")
    else:
        form = ShipForm()
    return render(request, "diary/add_ship.html", {"form": form})


# @login_required
# @with_user_language
# def calendar_2(request):
#     cal = HTMLCalendar().formatmonth(2017, 1)
#     return render(request, "diary/calendar2.html", {"cal": cal})


@login_required
@with_user_language
def google_calendar_init(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )
    flow.redirect_uri = request.build_absolute_uri('/oauth2callback/')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required
@with_user_language
def oauth2callback(request):
    # Ensure HTTPS is used in production
    if not settings.DEBUG:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
    else:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Verify state to prevent CSRF
    stored_state = request.session.get('oauth_state')
    if 'state' not in request.GET or request.GET['state'] != stored_state:
        raise SuspiciousOperation("State mismatch in OAuth callback")

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        state=stored_state
    )
    flow.redirect_uri = request.build_absolute_uri('/oauth2callback/')

    # Fetch token
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Store credentials in session
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # Clear the state from the session
    del request.session['oauth_state']

    return redirect('diary:calendar')


@login_required
@with_user_language
def calendar_g(request):
    if 'credentials' not in request.session:
        return redirect('diary:google_calendar_init')

    credentials = Credentials(
        token=request.session['credentials']['token'],
        refresh_token=request.session['credentials']['refresh_token'],
        token_uri=request.session['credentials']['token_uri'],
        client_id=request.session['credentials']['client_id'],
        client_secret=request.session['credentials']['client_secret']
    )

    try:
        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        logger.debug(f"Fetched {len(events)} events from Google Calendar")

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            formatted_event = {
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end
            }
            formatted_events.append(formatted_event)
            logger.debug(f"Event: {formatted_event}")

        # Update the stored credentials in case they were refreshed
        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        request.session.modified = True

        return render(request, 'diary/calendar.html', {'events': formatted_events})
    except RefreshError:
        # If refresh fails, redirect to re-authenticate
        logger.error("Failed to refresh credentials")
        return redirect('diary:google_calendar_init')


# @login_required
# @with_user_language
def get_ip(request):
    # First, try to get the IP from headers
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # If we're on localhost, try to get the external IP
    if ip == '127.0.0.1':
        try:
            external_ip = requests.get('https://api.ipify.org').text
            return external_ip
        except requests.RequestException:
            pass  # If the request fails, fall back to the original IP

    return ip


def get_location(request):
    a = "https://ipgeolocation.abstractapi.com/v1/?api_key=a999cf07aa444a6795b90c71c3e0e5f6&ip_address=188.69.184.99"
    user_ip = str(get_ip(request))
    response = requests.get(
        "https://ipgeolocation.abstractapi.com/v1/?api_key=" + ABSTRACT_GEO_KEY + "&ip_address=" + user_ip)

    all_data = json.loads(response.text)
    try:
        city = all_data["city"]
        latitude = all_data["latitude"]
        longitude = all_data["longitude"]
        return city, latitude, longitude
    except KeyError:
        error = "Error: Unable to fetch location data"
    return error


def get_weather_data(request):
    configuration = weatherapi.Configuration()
    configuration.api_key['key'] = WEATHER_API_KEY

    api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

    city, latitude, longitude, error = get_location(request)

    if error:
        q = error
    elif longitude and latitude:
        q = f"{latitude}/{longitude}"
    else:
        q = city

    selected_action = request.get('action_key')

    dt = 'laiko pasirinkimas'

    weather_api_actions = {
        1: (api_instance.astronomy, ['q', 'dt']),
        2: (api_instance.forecast_weather, ['q', 'days', 'dt', 'unixdt', 'hour', 'lang', 'alerts', 'aqi', 'tp']),
        3: (api_instance.future_weather, ['q', 'dt', 'lang',]),
        4: (api_instance.history_weather, ['q', 'dt', 'lang', 'unixdt', 'end_dt', 'unixend_dt', 'hour', 'lang']),
        5: (api_instance.ip_lookup, ['q']),
        6: (api_instance.marine_weather, ['q', 'dt', 'days', 'unixdt', 'hour', 'lang']),
        7: (api_instance.realtime_weather, ['q', 'lang',]),
        8: (api_instance.search_autocomplete_weather, ['q']),
        9: (api_instance.time_zone, ['q'])
    }

    if selected_action in weather_api_actions:
        action_function, required_parameters = weather_api_actions[selected_action]

        args = {}
        if 'q' in required_parameters:
            args['q'] = q
        if 'dt' in required_parameters:
            args['dt'] = dt

        weather_data = action_function(**args)
        return weather_data
    else:
        return "Error: Invalid action key"

# # @login_required
# # @with_user_language
# def show_weather(request):
#     client_location = get_ip(request)
#     get_lock = get_location(request)
#     get_w = get_weather(request)
#     #
#     # if client_location:
#     #     location_name = client_location.get("city", "Unknown")
#     #     try:
#     #         weather_response = get_weather(location_name)
#     #     except Exception as e:
#     #         logger.error(f"Error fetching weather for {location_name}: {e}")
#     #         weather_response = {"error": f"Unable to fetch weather data: {str(e)}"}
#     # else:
#     #     weather_response = {"error": "Unable to determine location"}
#     #
#     # context = {
#     #     "weather": weather_response,
#     #     "location": location_name
#     # }
#
#     context = {
#         "client_location": client_location,
#         "get_lock": get_lock,
#         "get_w": get_w,
#         "cache_key": cache
#     }
#
#     return render(request, 'diary/weather.html', context)
