from django import forms
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
)

from django.utils.translation import gettext_lazy as _


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
        fields = ["timestamp", "notes"]
        widgets = {
            "timestamp": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ShipForm(forms.ModelForm):
    class Meta:
        model = Ship
        fields = ["name", "type", "year_built"]


class EngineLogForm(forms.ModelForm):
    class Meta:
        model = EngineLog
        fields = "__all__"


class FuelLogForm(forms.ModelForm):
    class Meta:
        model = FuelLog
        fields = "__all__"


class MaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = "__all__"


class NavigationLogForm(forms.ModelForm):
    class Meta:
        model = NavigationLog
        fields = "__all__"


class WeatherLogForm(forms.ModelForm):
    class Meta:
        model = WeatherLog
        fields = "__all__"


class CrewLogForm(forms.ModelForm):
    class Meta:
        model = CrewLog
        fields = "__all__"
