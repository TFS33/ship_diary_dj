from __future__ import print_function
from datetime import datetime as dt
from time import sleep

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils import translation
from django.conf import settings
from django.views.decorators.http import require_POST
from google.auth.exceptions import RefreshError
from .forms import *
from django.core.mail import send_mail
from .helpers.weather_api.json_response_parse import (
    extract_forecast_data,
    extract_marine_data,
)
from .models import CustomUser, LogEntry, Ship, WeatherData
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.urls import translate_url, reverse
import logging
from django.utils.translation import gettext as _
from .helpers.middleware.decorator import with_user_language
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
from django.contrib import messages



logger = logging.getLogger(__name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # for HTTP


@with_user_language
def index(request):
    return render(
        request,
        "diary/index.html",
    )


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

            messages.success(request, _('Your account has been created! You are now able to log in'))


            return redirect("diary:user_home")
    else:
        form = CustomUserForm()
    return render(
        request,
        "diary/register.html",
        {
            "form": form,
        },
    )


@login_required
@with_user_language
def user_home(request):
    user = get_object_or_404(CustomUser, pk=request.user.id)

    return render(
        request,
        "diary/user_home.html",
        {
            "user": user,
        },
    )


@login_required
@with_user_language
def log_out(request):
    logout(request)
    messages.success(request, _('You are now logged out'))
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
                messages.success(request, _('You are now logged in, welcome back!'))
                sleep(2)
                return redirect("diary:user_home")
            else:
                messages.error(request, _('Invalid email or password'))
        else:
            messages.error(request, _('Please correct the errors below'))
    else:
        form = LoginForm()

    return render(request, "diary/login.html", {"form": form})


@login_required
@with_user_language
def records(request):
    records_data = LogEntry.objects.filter(created_by=request.user).order_by(
        "created_at"
    )
    return render(request, "diary/records.html", {"records_data": records_data})


@login_required
@with_user_language
def ship(request):
    ship_data = Ship.objects.filter(owner=request.user).order_by("created_at")

    return render(request, "diary/ship.html", {"ship_data": ship_data})


@login_required
@with_user_language
def set_language(request):
    language = request.POST.get("language", settings.LANGUAGE_CODE)
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect(reverse("diary:user_home"))


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


@login_required
@with_user_language
def edit_ship_data(request, ship_id):
    ship = get_object_or_404(Ship, pk=ship_id, owner=request.user)
    if request.method == "POST":
        form = ShipForm(request.POST, instance=ship)
        if form.is_valid():
            ship = form.save(commit=False)
            ship.save()
            return redirect("diary:ship")
    else:
        form = ShipForm(instance=ship)
    return render(request, "diary/edit_ship.html", {"form": form, "ship": ship})


@login_required
def delete_ship(request, ship_id):
    ship = get_object_or_404(Ship, pk=ship_id, owner=request.user)
    ship.delete()
    return redirect("diary:ship")


# @login_required
# @with_user_language
# def calendar_2(request):
#     cal = HTMLCalendar().formatmonth(2017, 1)
#     return render(request, "diary/calendar2.html", {"cal": cal})


@login_required
@with_user_language
def add_log_entry(request):
    if request.method == "POST":
        form = LogEntryForm(request.POST, user=request.user)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.created_by = request.user
            log_entry.save()
            return redirect("diary:view_log_entries")
    else:
        form = LogEntryForm(user=request.user)
    return render(request, "diary/add_log_entry.html", {"form": form})


@login_required
@with_user_language
def view_logs(request):
    logs = LogEntry.objects.filter(created_by=request.user).order_by("timestamp")
    return render(request, "diary/log_list.html", {"logs": logs})


@login_required
@with_user_language
def edit_log(request, log_id):
    log = get_object_or_404(LogEntry, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = LogEntryForm(request.POST, instance=log)
        if form.is_valid():
            log = form.save(commit=False)
            log.save()
            return redirect("diary:view_log_entries")
    else:
        form = LogEntryForm(instance=log)
    return render(request, "diary/edit_log.html", {"form": form, "log": log})


@login_required
def delete_log(request, log_id):
    log = get_object_or_404(LogEntry, pk=log_id, created_by=request.user)
    log.delete()
    return redirect("diary:view_log_entries")


@login_required
@with_user_language
def google_calendar_init(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
    flow.redirect_uri = request.build_absolute_uri("/oauth2callback/")
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    request.session["oauth_state"] = state
    return redirect(authorization_url)


@login_required
@with_user_language
def oauth2callback(request):
    # Ensure HTTPS is used in production
    if not settings.DEBUG:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
    else:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Verify state to prevent CSRF
    stored_state = request.session.get("oauth_state")
    if "state" not in request.GET or request.GET["state"] != stored_state:
        raise SuspiciousOperation("State mismatch in OAuth callback")

    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        state=stored_state,
    )
    flow.redirect_uri = request.build_absolute_uri("/oauth2callback/")

    # Fetch token
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Store credentials in session
    request.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # Clear the state from the session
    del request.session["oauth_state"]

    return redirect("diary:calendar")


@login_required
@with_user_language
def calendar_g(request):
    if "credentials" not in request.session:
        return redirect("diary:google_calendar_init")

    credentials = Credentials(
        token=request.session["credentials"]["token"],
        refresh_token=request.session["credentials"]["refresh_token"],
        token_uri=request.session["credentials"]["token_uri"],
        client_id=request.session["credentials"]["client_id"],
        client_secret=request.session["credentials"]["client_secret"],
    )

    try:
        service = build("calendar", "v3", credentials=credentials)
        events_result = (
            service.events().list(calendarId="primary", maxResults=10).execute()
        )
        events = events_result.get("items", [])

        logger.debug(f"Fetched {len(events)} events from Google Calendar")

        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            formatted_event = {
                "summary": event.get("summary", "No Title"),
                "start": start,
                "end": end,
            }
            formatted_events.append(formatted_event)
            logger.debug(f"Event: {formatted_event}")

        # Update the stored credentials in case they were refreshed
        request.session["credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }
        request.session.modified = True

        return render(request, "diary/calendar.html", {"events": formatted_events})
    except RefreshError:
        # If refresh fails, redirect to re-authenticate
        logger.error("Failed to refresh credentials")
        return redirect("diary:google_calendar_init")


# @login_required
# @with_user_language
# def get_ip(request):
#     # First, try to get the IP from headers
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#
#     # If we're on localhost, try to get the external IP
#     if ip == '127.0.0.1':
#         try:
#             external_ip = requests.get('https://api.ipify.org').text
#             return external_ip
#         except requests.RequestException:
#             pass  # If the request fails, fall back to the original IP
#
#     return ip


def get_ip(request):
    logger.debug("Entering get_ip function")

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    logger.debug(f"Initial IP detected: {ip}")

    if ip == "127.0.0.1":
        try:
            external_ip = requests.get("https://api.ipify.org").text
            logger.debug(f"External IP detected: {external_ip}")
            return external_ip
        except requests.RequestException as e:
            logger.error(f"Error getting external IP: {str(e)}")
            return ip

    return ip


def get_location(request):
    user_ip = str(get_ip(request))

    try:
        response = requests.get(
            "https://ipgeolocation.abstractapi.com/v1/?api_key="
            + ABSTRACT_GEO_KEY
            + "&ip_address="
            + user_ip
        )
        logger.debug(f"API Response status code: {response.status_code}")
        logger.debug(f"API Response content: {response.text}")

        all_data = json.loads(response.text)
        city = all_data.get("city", "Unknown")
        latitude = all_data.get("latitude", 0)
        longitude = all_data.get("longitude", 0)

        return city, latitude, longitude

    except json.JSONDecodeError as e:
        return f"{e}"


def get_realtime_weather_data(request):
    try:
        location_result = get_location(request)
        if isinstance(location_result, str):  # Error was returned
            return f"Error: Unable to determine location - {location_result}"

        city, latitude, longitude = location_result
        cache_key = f"weather_data_{city}_{latitude}_{longitude}"

        # Try to get data from cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        configuration = weatherapi.Configuration()
        configuration.api_key["key"] = WEATHER_API_KEY
        api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

        city = get_location(request)
        if city != "Error: Unable to fetch location data klaida ties city":
            try:
                api_response = api_instance.realtime_weather(q=city)
                return api_response
            except ApiException as e:
                return {
                    "error": "Error: Nepavyko gaut prognozes klaida ties api response"
                }

    except Exception as e:
        return f"Error: {str(e)}"


def get_astronomy_data(request):
    form = AstronomyWeatherApiForm()

    if request.method == "POST":
        form = AstronomyWeatherApiForm(request.POST)
        configuration = weatherapi.Configuration()
        configuration.api_key["key"] = WEATHER_API_KEY
        api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))
        if form.is_valid():
            q = form.cleaned_data["q"]
            dt = form.cleaned_data["dt"]
            try:
                # response = requests.get(
                #     f"https://api.weatherapi.com/v1/astronomy.json?key={WEATHER_API_KEY}&q={q}&dt={dt}"
                # )
                response = api_instance.astronomy(q=q, dt=dt)

                if response is not None or response != "403":
                    all_data = response
                    location = all_data.get("location")
                    region = location.get("region")

                    astronomy = all_data.get("astronomy")
                    astro = astronomy.get("astro")
                    sunrise = astro.get("sunrise")
                    sunset = astro.get("sunset")
                    moonrise = astro.get("moonrise")
                    moonset = astro.get("moonset")
                    moon_phase = astro.get("moon_phase")
                    moon_iliumination = astro.get("moon_illumination")
                    is_moon_up = astro.get("is_moon_up")
                    is_sun_ip_up = astro.get("is_sun_up")

                    context = {
                        "region": region,
                        "sunrise": sunrise,
                        "sunset": sunset,
                        "moonrise": moonrise,
                        "moonset": moonset,
                        "moon_phase": moon_phase,
                        "moon_iliumination": moon_iliumination,
                        "is_moon_up": is_moon_up,
                        "is_sun_ip_up": is_sun_ip_up,
                        "form": form,
                    }

                    return render(request, "diary/astronomy.html", context)
                else:
                    return render(
                        request,
                        "diary/astronomy.html",
                        {"form": form, "error": (_("Invalid form data"))},
                    )

            except requests.RequestException as e:
                return render(
                    request,
                    "diary/astronomy.html",
                    {"form": form, e: (_("500 Internal Server Error"))},
                )
            except json.JSONDecodeError as e:
                return render(
                    request,
                    "diary/astronomy.html",
                    {"form": form, e: (_("Json Decode Error"))},
                )
        else:
            return render(
                request,
                "diary/astronomy.html",
                {"form": form, "form_error": (_("Invalid form data"))},
            )

    return render(request, "diary/astronomy.html", {"form": form})


@login_required
@with_user_language
def show_weather(request):
    location_result = get_location(request)
    context = {}

    if isinstance(location_result, str):
        context["error"] = f"Location error: {location_result}"
    else:
        city, latitude, longitude = location_result
        context = {"city": city, "latitude": latitude, "longitude": longitude}

        weather_data = get_realtime_weather_data(request)
        if isinstance(weather_data, str) and weather_data.startswith("Error"):
            context["error"] = weather_data
        else:
            context["weather_data"] = weather_data
    return render(request, "diary/weather.html", context)


@login_required
def get_forecast_data(request):
    form = ForecastWeatherApiForm()
    context = {"form": form}

    if request.method == "POST":
        form = ForecastWeatherApiForm(request.POST)
        if form.is_valid():
            configuration = weatherapi.Configuration()
            configuration.api_key["key"] = WEATHER_API_KEY
            api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

            try:
                response = api_instance.forecast_weather(
                    q=form.cleaned_data["q"],
                    days=form.cleaned_data["days"],
                    dt=form.cleaned_data["dt"],
                    unixdt=form.cleaned_data["unixdt"],
                    hour=form.cleaned_data["hour"],
                    lang=form.cleaned_data["lang"],
                    alerts=form.cleaned_data["alerts"],
                    aqi=form.cleaned_data["aqi"],
                    tp=form.cleaned_data["tp"],
                )

                processed_data = extract_forecast_data(response)
                context.update(
                    {"weather_data": processed_data, "raw_response": response}
                )
                logger.debug(processed_data)

            except ApiException as e:
                context["error"] = f"API Error: {str(e)}"
            except Exception as e:
                context["error"] = f"Unexpected error: {str(e)}"

        else:
            context["error"] = "Invalid form data"

    return render(request, "diary/forecast.html", context)


@login_required
@with_user_language
def get_marine_data(request):
    form = MarineWeatherApiForm
    context = {"form": form}

    if request.method == "POST":
        form = MarineWeatherApiForm(request.POST)
        if form.is_valid():
            configuration = weatherapi.Configuration()
            configuration.api_key["key"] = WEATHER_API_KEY
            api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

            try:
                response = api_instance.marine_weather(
                    q=form.cleaned_data["q"],
                    days=form.cleaned_data["days"],
                    dt=form.cleaned_data["dt"],
                    unixdt=form.cleaned_data["unixdt"],
                    hour=form.cleaned_data["hour"],
                    lang=form.cleaned_data["lang"],
                )

                processed_data = extract_marine_data(response)
                context.update(
                    {"weather_data": processed_data, "raw_response": response}
                )

                request.session["weather_data"] = processed_data

            except ApiException as e:
                context["error"] = f"API Error: {str(e)}"
            except Exception as e:
                context["error"] = f"Unexpected error: {str(e)}"

        else:
            context["error"] = "Invalid form data"

    return render(request, "diary/marine.html", context)


@login_required
@with_user_language
def add_engine_log(request):
    if request.method == "POST":
        form = EngineLogForm(request.POST, user=request.user)
        if form.is_valid():
            engine_log = form.save(commit=False)
            engine_log.save()
            return redirect("diary:view_engine_logs")
    else:
        form = EngineLogForm(user=request.user)
    return render(request, "diary/add_engine_log.html", {"form": form})


@login_required
@with_user_language
def view_engine_logs(request):
    engine_logs = EngineLog.objects.filter(created_by=request.user).order_by(
        "timestamp"
    )
    return render(request, "diary/engine_log_list.html", {"engine_logs": engine_logs})


@login_required
def delete_engine_log(request, log_id):
    engine_log = get_object_or_404(EngineLog, pk=log_id, created_by=request.user)
    engine_log.delete()
    return redirect("diary:view_engine_logs")


@login_required
@with_user_language
def edit_engine_log(request, log_id):
    engine_log = get_object_or_404(EngineLog, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = EngineLogForm(request.POST, instance=engine_log)
        if form.is_valid():
            engine_log = form.save(commit=False)
            engine_log.save()
            return redirect("diary:view_engine_logs")
    else:
        form = EngineLogForm(instance=engine_log)
    return render(
        request, "diary/edit_engine_log.html", {"form": form, "engine_log": engine_log}
    )


@login_required
@with_user_language
def add_fuel_log(request):
    if request.method == "POST":
        form = FuelLogForm(request.POST, user=request.user)
        if form.is_valid():
            fuel_log = form.save(commit=False)
            fuel_log.save()
            return redirect("diary:view_fuel_logs")
    else:
        form = FuelLogForm(user=request.user)
    return render(request, "diary/add_fuel_log.html", {"form": form})


@login_required
@with_user_language
def view_fuel_logs(request):
    fuel_log = FuelLog.objects.filter(created_by=request.user).order_by("timestamp")
    return render(request, "diary/fuel_log_list.html", {"fuel_log": fuel_log})


@login_required
def delete_fuel_log(request, log_id):
    fuel_log = get_object_or_404(FuelLog, pk=log_id, created_by=request.user)
    fuel_log.delete()
    return redirect("diary:view_fuel_logs")


@login_required
@with_user_language
def edit_fuel_log(request, log_id):
    fuel_log = get_object_or_404(FuelLog, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = FuelLogForm(request.POST, instance=fuel_log)
        if form.is_valid():
            fuel_log = form.save(commit=False)
            fuel_log.save()
            return redirect("diary:view_fuel_logs")
    else:
        form = FuelLogForm(instance=fuel_log)
    return render(
        request, "diary/edit_fuel_log.html", {"form": form, "fuel_log": fuel_log}
    )


@login_required
@with_user_language
def add_navi_log(request):
    if request.method == "POST":
        form = NavigationLogForm(request.POST, user=request.user)
        if form.is_valid():
            navi_log = form.save(commit=False)
            navi_log.save()
            return redirect("diary:view_navi_logs")
    else:
        form = NavigationLogForm(user=request.user)
    return render(request, "diary/add_navi_log.html", {"form": form})


@login_required
@with_user_language
def view_navi_logs(request):
    navi_log = NavigationLog.objects.filter(created_by=request.user).order_by(
        "timestamp"
    )
    return render(request, "diary/navi_log_list.html", {"navi_log": navi_log})


@login_required
@with_user_language
def edit_navi_log(request, log_id):
    navi_log = get_object_or_404(NavigationLog, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = NavigationLogForm(request.POST, instance=navi_log)
        if form.is_valid():
            navi_log = form.save(commit=False)
            navi_log.save()
            return redirect("diary:view_navi_logs")
    else:
        form = NavigationLogForm(instance=navi_log)
    return render(
        request, "diary/edit_navi_log.html", {"form": form, "navi_log": navi_log}
    )


@login_required
def delete_navi_log(request, log_id):
    navi_log = get_object_or_404(NavigationLog, pk=log_id, created_by=request.user)
    navi_log.delete()
    return redirect("diary:view_navi_logs")


@login_required
@with_user_language
def add_crew_log(request):
    if request.method == "POST":
        form = CrewLogForm(request.POST, user=request.user)
        if form.is_valid():
            crew_log = form.save(commit=False)
            crew_log.save()
            return redirect("diary:view_crew_logs")
    else:
        form = CrewLogForm(user=request.user)
    return render(request, "diary/add_crew_log.html", {"form": form})


@login_required
@with_user_language
def edit_crew_log(request, log_id):
    crew_log = get_object_or_404(CrewLog, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = FuelLogForm(request.POST, instance=crew_log)
        if form.is_valid():
            crew_log = form.save(commit=False)
            crew_log.save()
            return redirect("diary:view_crew_logs")
    else:
        form = FuelLogForm(instance=crew_log)
    return render(
        request, "diary/edit_crew_log.html", {"form": form, "crew_log": crew_log}
    )


@login_required
@with_user_language
def view_crew_logs(request):
    crew_log = CrewLog.objects.filter(created_by=request.user).order_by("timestamp")
    return render(request, "diary/crew_log_list.html", {"crew_log": crew_log})


@login_required
def delete_crew_log(request, log_id):
    crew_log = get_object_or_404(CrewLog, pk=log_id, created_by=request.user)
    crew_log.delete()
    return redirect("diary:view_crew_logs")


@login_required
@with_user_language
def add_weather_log(request):
    if request.method == "POST":
        form = WeatherLogForm(request.POST, user=request.user)
        if form.is_valid():
            weather_log = form.save(commit=False)
            weather_log.save()
            return redirect("diary:view_weather_logs")
    else:
        form = WeatherLogForm(user=request.user)
    return render(request, "diary/add_weather_log.html", {"form": form})


@login_required
@with_user_language
def edit_weather_log(request, log_id):
    weather_log = get_object_or_404(WeatherLog, pk=log_id, created_by=request.user)
    if request.method == "POST":
        form = WeatherLogForm(request.POST, instance=weather_log)
        if form.is_valid():
            weather_log = form.save(commit=False)
            weather_log.save()
            return redirect("diary:view_weather_logs")
    else:
        form = WeatherLogForm(instance=weather_log)
    return render(
        request,
        "diary/edit_weather_log.html",
        {"form": form, "weather_log": weather_log},
    )


@login_required
@with_user_language
def view_weather_logs(request):
    weather_log = WeatherLog.objects.filter(created_by=request.user).order_by(
        "timestamp"
    )
    return render(request, "diary/weather_log_list.html", {"weather_log": weather_log})


@login_required
def delete_weather_log(request, log_id):
    weather_log = get_object_or_404(WeatherLog, pk=log_id, created_by=request.user)
    weather_log.delete()
    return redirect("diary:view_weather_logs")


@login_required
@with_user_language
def add_maintenance_log(request):
    if request.method == "POST":
        form = MaintenanceLogForm(request.POST, user=request.user)
        if form.is_valid():
            maintenance_log = form.save(commit=False)
            maintenance_log.save()
            return redirect("diary:view_maintenance_logs")
    else:
        form = MaintenanceLogForm(user=request.user)
    return render(request, "diary/add_maintenance_log.html", {"form": form})


@login_required
@with_user_language
def edit_maintenance_log(request, log_id):
    maintenance_log = get_object_or_404(
        MaintenanceLog, pk=log_id, created_by=request.user
    )
    if request.method == "POST":
        form = MaintenanceLogForm(request.POST, instance=maintenance_log)
        if form.is_valid():
            maintenance_log = form.save(commit=False)
            maintenance_log.save()
            return redirect("diary:view_maintenance_logs")
    else:
        form = MaintenanceLogForm(instance=maintenance_log)
    return render(
        request,
        "diary/edit_maintenance_log.html",
        {"form": form, "maintenance_log": maintenance_log},
    )


@login_required
@with_user_language
def view_maintenance_logs(request):
    maintenance_log = MaintenanceLog.objects.filter(created_by=request.user).order_by(
        "timestamp"
    )
    return render(
        request, "diary/maintenance_log_list.html", {"maintenance_log": maintenance_log}
    )


@login_required
def delete_maintenance_log(request, log_id):
    maintenance_log = get_object_or_404(
        MaintenanceLog, pk=log_id, created_by=request.user
    )
    maintenance_log.delete()
    return redirect("diary:view_maintenance_logs")


@login_required
@with_user_language
def ship_logs_all(request):
    ships = Ship.objects.all()

    # Get the ship_id from the GET parameters
    ship_id = request.GET.get("ship_id")

    if ship_id:
        ship = get_object_or_404(Ship, id=ship_id)
        logs = LogEntry.objects.filter(ship=ship).order_by("-timestamp")

        # Categorize logs by type
        categorized_logs = {
            "engine_logs": logs.filter(enginelog__isnull=False),
            "fuel_logs": logs.filter(fuellog__isnull=False),
            "navigation_logs": logs.filter(navigationlog__isnull=False),
            "crew_logs": logs.filter(crewlog__isnull=False),
            "weather_logs": logs.filter(weatherlog__isnull=False),
            "maintenance_logs": logs.filter(maintenancelog__isnull=False),
        }
    else:
        ship = None
        logs = []
        categorized_logs = {}

    context = {
        "ships": ships,
        "selected_ship": ship,
        "logs": logs,
        "categorized_logs": categorized_logs,
    }
    return render(request, "diary/get_all_ship_logs.html", context)


# @login_required
# def save_weather_api_to_db(request):
#     if request.method == "POST":
#         try:
#             data_for_forecast = request.POST.get("forecast_data")
#             data_for_location = request.POST.get("location_data")
#             data_for_weather = request.session.get("weather_data", {})
#
#             location = data_for_weather.get("location", {})
#             forecast = None
#
#             for day in data_for_weather.get("forecast", []):
#                 if day["date"] == data_for_forecast:
#                     forecast = day
#                     break
#
#             if forecast is None:
#                 messages.error(request, _('No forecast data'))
#                 return redirect("diary:show_weather")
#
#             weather_data = WeatherData(
#                 location_name=data_for_location,
#                 location_region=location.get("region", ""),
#                 location_country=location.get("country", ""),
#                 latitude=location.get("lat", 0),
#                 longitude=location.get("lon", 0),
#                 date=forecast["date"],
#                 max_temp=forecast["maxtemp_c"],
#                 min_temp=forecast["mintemp_c"],
#                 avg_temp=forecast["avgtemp_c"],
#                 max_wind=forecast["maxwind_kph"],
#                 total_precip=forecast["totalprecip_mm"],
#                 total_snow=forecast["totalsnow_cm"],
#                 avg_visibility=forecast["avgvis_km"],
#                 avg_humidity=forecast["avghumidity"],
#                 uv_index=forecast["uv"],
#                 sunrise=correcting_time(forecast["astro"]["sunrise"]),
#                 sunset=correcting_time(forecast["astro"]["sunset"]),
#                 moonrise=correcting_time(forecast["astro"]["moonrise"]),
#                 moonset=correcting_time(forecast["astro"]["moonset"]),
#                 moon_phase=forecast["astro"]["moon_phase"],
#             )
#             weather_data.save()
#
#         except Exception as e:
#             messages.error(request, f"str{e}")
#             return redirect("diary:marine_forecast")
#
#         messages.success(request, _("Weather data saved"))
#         return redirect("diary:marine_forecast")
#
#     else:
#         messages.error(request, _("No data received"))
#         return redirect("diary:marine_forecast")


@login_required
@require_POST
def save_weather_api_to_db(request):
    try:
        data_for_forecast = request.POST.get("forecast_data")
        data_for_location = request.POST.get("location_data")
        data_for_weather = request.session.get("weather_data", {})

        location = data_for_weather.get("location", {})
        forecast = None

        for day in data_for_weather.get("forecast", []):
            if day["date"] == data_for_forecast:
                forecast = day
                break

        if forecast is None:
            messages.error(request, _("No forecast data"))

        weather_data = WeatherData(
            location_name=data_for_location,
            location_region=location.get("region", ""),
            location_country=location.get("country", ""),
            latitude=location.get("lat", 0),
            longitude=location.get("lon", 0),
            date=forecast["date"],
            max_temp=forecast["maxtemp_c"],
            min_temp=forecast["mintemp_c"],
            avg_temp=forecast["avgtemp_c"],
            max_wind=forecast["maxwind_kph"],
            total_precip=forecast["totalprecip_mm"],
            total_snow=forecast["totalsnow_cm"],
            avg_visibility=forecast["avgvis_km"],
            avg_humidity=forecast["avghumidity"],
            uv_index=forecast["uv"],
            sunrise=correcting_time(forecast["astro"]["sunrise"]),
            sunset=correcting_time(forecast["astro"]["sunset"]),
            moonrise=correcting_time(forecast["astro"]["moonrise"]),
            moonset=correcting_time(forecast["astro"]["moonset"]),
            moon_phase=forecast["astro"]["moon_phase"],
        )
        weather_data.save()

        messages.success(request, _("Weather data saved"))
        sleep(3)
        return redirect("diary:saved_marine_api_logs")

    except Exception as e:
        messages.error(request, f"str{e}")

def correcting_time(time):
    time = dt.strptime(time, "%I:%M %p")
    return time.strftime("%H:%M")


@login_required
@with_user_language
def show_w_api_list(request):
    logs = WeatherData.objects.all()
    return render(request, "diary/weather_api_list.html", {"logs": logs})
