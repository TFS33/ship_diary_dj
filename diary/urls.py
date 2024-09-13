from django.urls import path
from . import views
from django.utils.translation import gettext_lazy as _

app_name = "diary"

urlpatterns = [
    path("", views.index, name="index"),
    path(_("register/"), views.register, name="register"),
    path(_("user_home/"), views.user_home, name="user_home"),
    path(_("login/"), views.log_in, name="login"),
    path(_("logout/"), views.log_out, name="logout"),
    path(_('records/'), views.records, name='records'),
    path(_('ship/'), views.ship, name='ship'),
    path('set_language/', views.set_language, name='set_language'),
    path(_('add_ship/'), views.add_ship, name='add_ship'),
    path(_('calendar/'), views.calendar_g, name='calendar'),
    path('google_calendar_init/', views.google_calendar_init, name='google_calendar_init'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('get_location/', views.get_ip, name='get_location'),
    path('show_weather/', views.show_weather, name='show_weather'),
    path('get_weather/', views.get_weather, name='get_weather'),
]
