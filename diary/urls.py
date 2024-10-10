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
    path(_("records/"), views.records, name="records"),
    path(_("ship/"), views.ship, name="ship"),
    path("set_language/", views.set_language, name="set_language"),
    path(_("add_ship/"), views.add_ship, name="add_ship"),
    path(_("calendar/"), views.calendar_g, name="calendar"),
    path(
        "google_calendar_init/", views.google_calendar_init, name="google_calendar_init"
    ),
    path("oauth2callback/", views.oauth2callback, name="oauth2callback"),
    path("get_location/", views.get_ip, name="get_location"),
    path("get_weather/", views.show_weather, name="show_weather"),
    path("get_astronomy/", views.get_astronomy_data, name="get_astronomy"),
    path("get_forecast/", views.get_forecast_data, name="get_forecast"),
    path("add_log_entry/", views.add_log_entry, name="add_log_entry"),
    path("get_log_entries/", views.view_logs, name="view_log_entries"),
    path("edit_log_entry/<int:log_id>/", views.edit_log, name="edit_log_entry"),
    path("delete_log_entry/<int:log_id>/", views.delete_log, name="delete_log_entry"),
    path("edit_ship/<int:ship_id>/", views.edit_ship_data, name="edit_ship"),
    path("delete_ship/<int:ship_id>", views.delete_ship, name="delete_ship"),
    path("add_engine_log/", views.add_engine_log, name="add_engine_log"),
    path("ship/logs/", views.ship_logs_all, name="ship_logs_all"),
    path("engine/logs/add", views.add_engine_log, name="add_engine_log"),
    path("engine/logs/", views.view_engine_logs, name="view_engine_logs"),
    path(
        "engine/delete/<int:log_id>/", views.delete_engine_log, name="delete_engine_log"
    ),
    path("engine/edit/<int:log_id>/", views.edit_engine_log, name="edit_engine_log"),
    path("fuel/add_log/", views.add_fuel_log, name="add_fuel_log"),
    path("fuel/logs/", views.view_fuel_logs, name="view_fuel_logs"),
    path("fuel/delete/<int:log_id>/", views.delete_fuel_log, name="delete_fuel_log"),
    path("fuel/edit/<int:log_id>/", views.edit_fuel_log, name="edit_fuel_log"),
    path("navigation/add", views.add_navi_log, name="navigation_add"),
    path("navigation/logs/", views.view_navi_logs, name="view_navi_logs"),
    path(
        "navigation/delete/<int:log_id>/", views.delete_navi_log, name="delete_navi_log"
    ),
    path("navigation/edit/<int:log_id>/", views.edit_navi_log, name="edit_navi_log"),
    path("crew/add_log/", views.add_crew_log, name="add_crew_log"),
    path("crew/logs/", views.view_crew_logs, name="view_crew_logs"),
    path("crew/delete/<int:log_id>/", views.delete_crew_log, name="delete_crew_log"),
    path("crew/edit/<int:log_id>/", views.edit_crew_log, name="edit_crew_log"),
    path("weather/add_log/", views.add_weather_log, name="add_weather_log"),
    path("weather/logs/", views.view_weather_logs, name="view_weather_logs"),
    path(
        "weather/delete/<int:log_id>/",
        views.delete_weather_log,
        name="delete_weather_log",
    ),
    path("weather/edit/<int:log_id>/", views.edit_weather_log, name="edit_weather_log"),
    path("maintenance/add_log/", views.add_maintenance_log, name="add_maintenance_log"),
    path(
        "maintenance/logs/", views.view_maintenance_logs, name="view_maintenance_logs"
    ),
    path(
        "maintenance/delete/<int:log_id>/",
        views.delete_maintenance_log,
        name="delete_maintenance_log",
    ),
    path(
        "maintenance/edit/<int:log_id>/",
        views.edit_maintenance_log,
        name="edit_maintenance_log",
    ),
    path("marine_forecast/", views.get_marine_data, name="marine_forecast"),
    path(
        "marine_forecast/save_to_database/",
        views.save_weather_api_to_db,
        name="save_to_database_marine_api",
    ),
    path("saved_marine_logs/", views.show_w_api_list, name="saved_marine_api_logs"),
]
