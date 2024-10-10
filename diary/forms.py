from django import forms
from django.forms import DateInput

from .models import (
    LogEntry,
    Ship,
    EngineLog,
    FuelLog,
    MaintenanceLog,
    NavigationLog,
    WeatherLog,
    CrewLog,
    CustomUser,
    get_ship_choices,
)

from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "confirm_password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get(_("password"))
        confirm_password = cleaned_data.get(_("confirm_password"))

        if password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match"))

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    fields = ["email", "password"]


class LogEntryForm(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = ["ship", "timestamp", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )


class ShipForm(forms.ModelForm):
    class Meta:
        model = Ship
        fields = ["name", "type", "year_built"]


class EngineLogForm(forms.ModelForm):
    class Meta:
        model = EngineLog
        fields = [
            "ship",
            "hours_operated",
            "fuel_consumed",
            "maintenance_notes",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class FuelLogForm(forms.ModelForm):
    class Meta:
        model = FuelLog
        fields = ["ship", "current_level", "consumed", "refilled"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class MaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = [
            "ship",
            "equipment",
            "work_done",
            "hours_worked",
            "minutes_worked",
            "next_maintenance",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class NavigationLogForm(forms.ModelForm):
    class Meta:
        model = NavigationLog
        fields = ["ship", "latitude", "longitude", "destination", "speed"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class WeatherLogForm(forms.ModelForm):
    class Meta:
        model = WeatherLog
        fields = [
            "ship",
            "temperature",
            "wind_speed",
            "wind_direction",
            "waterway_state",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class CrewLogForm(forms.ModelForm):
    class Meta:
        model = CrewLog
        fields = ["ship", "crew_count", "crew_changes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["ship"].queryset = Ship.objects.filter(
                Ship.get_user_ships(self.user)
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


api_language_choices = (
    ("en", "English"),
    ("ar", "Arabic"),
    ("bn", "Bengali"),
    ("bg", "Bulgarian"),
    ("zh", "Chinese Simplified"),
    ("zh_tw", "Chinese Traditional"),
    ("cs", "Czech"),
    ("da", "Danish"),
    ("nl", "Dutch"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("de", "German"),
    ("el", "Greek"),
    ("hi", "Hindi"),
    ("hu", "Hungarian"),
    ("it", "Italian"),
    ("ja", "Japanese"),
    ("jv", "Javanese"),
    ("ko", "Korean"),
    ("zh_cmn", "Mandarin"),
    ("mr", "Marathi"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("pa", "Punjabi"),
    ("ro", "Romanian"),
    ("ru", "Russian"),
    ("sr", "Serbian"),
    ("si", "Sinhala"),
    ("sk", "Slovak"),
    ("es", "Spanish"),
    ("sv", "Swedish"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("ur", "Urdu"),
    ("vi", "Vietnamese"),
    ("zh_wuu", "Wu (Shanghainese)"),
    ("zh_hsn", "Xiang"),
    ("zh_yue", "Yue (Cantonese)"),
    ("zu", "Zulu"),
)


class WeatherApiForm(forms.Form):
    q = forms.CharField()
    days = forms.IntegerField(required=False, max_value=3)
    dt = forms.DateField(
        widget=DateInput(attrs={"type": "date", "format": "%Y-%m-%d"}), required=False
    )
    unixdt = forms.IntegerField(required=False)
    hour = forms.IntegerField(required=False)
    lang = forms.ChoiceField(
        choices=api_language_choices,
        required=False,
    )  # initial=None)
    alerts = forms.BooleanField(required=False)
    aqi = forms.BooleanField(required=False)
    tp = forms.IntegerField(required=False)
    end_dt = forms.DateTimeField(required=False)
    unixend_dt = forms.IntegerField(required=False)


class RealtimeWeatherApiForm(WeatherApiForm):
    class Meta:
        fields = ["q", "lang"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_fields = ["q", "dt"]
        for field in list(self.fields.keys()):
            if field not in allowed_fields:
                del self.fields[field]


class ForecastWeatherApiForm(WeatherApiForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_fields = [
            "q",
            "days",
            "dt",
            "unixdt",
            "hour",
            "lang",
            "alerts",
            "aqi",
            "tp",
        ]
        for field in list(self.fields.keys()):
            if field not in allowed_fields:
                del self.fields[field]


class FutureWeatherApiForm(WeatherApiForm):
    class Meta:
        fields = ["q", "dt", "lang"]


class HistoryWeatherApiForm(WeatherApiForm):
    class Meta:
        fields = ["q", "dt", "unixdt", "end_dt", "unixend_dt", "hour", "lang"]


class AstronomyWeatherApiForm(WeatherApiForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_fields = ["q", "dt"]
        for field in list(self.fields.keys()):
            if field not in allowed_fields:
                del self.fields[field]


class MarineWeatherApiForm(WeatherApiForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_fields = ["q", "days", "dt", "unixdt", "hour", "lang"]
        for field in list(self.fields.keys()):
            if field not in allowed_fields:
                del self.fields[field]
