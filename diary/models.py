from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from diary.managers import CustomUserManager
from django.conf import settings


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=100, unique=True)
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    user_set_language = models.CharField(_("language"), max_length=100, choices=settings.LANGUAGES,
                                         default=settings.LANGUAGE_CODE)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Ship(BaseModel):
    name = models.CharField(_("Name"), max_length=100)
    type = models.CharField(_("Type"), max_length=100)
    year_built = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ships",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} - {self.type} ({self.year_built})"


class LogEntry(BaseModel):
    ship = models.ForeignKey(
        Ship,
        on_delete=models.CASCADE,
        related_name="log_entries",
        verbose_name=_("Ship"),
    )
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(_("Notes"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="log_entries"
    )

    def __str__(self):
        return f"{self.timestamp} - {self.ship.name}: {self.notes[:30]}..."


class EngineLog(LogEntry):
    hours_operated = models.FloatField(
        _("Hours Operated"), validators=[MinValueValidator(0)]
    )
    fuel_consumed = models.FloatField(
        _("Fuel Consumed"), validators=[MinValueValidator(0)]
    )
    maintenance_notes = models.TextField(_("Maintenance Notes"), blank=True)


class FuelLog(LogEntry):
    current_level = models.FloatField(validators=[MinValueValidator(0)])
    consumed = models.FloatField(validators=[MinValueValidator(0)])
    refilled = models.FloatField(validators=[MinValueValidator(0)])


class NavigationLog(LogEntry):
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    speed = models.FloatField(validators=[MinValueValidator(0)])
    destination = models.CharField(max_length=200)


class CrewLog(LogEntry):
    crew_count = models.IntegerField(validators=[MinValueValidator(0)])
    crew_changes = models.TextField(blank=True)


class WeatherLog(LogEntry):
    WIND_DIRECTIONS = [
        ("N", "North"),
        ("NE", "Northeast"),
        ("E", "East"),
        ("SE", "Southeast"),
        ("S", "South"),
        ("SW", "Southwest"),
        ("W", "West"),
        ("NW", "Northwest"),
    ]
    WATER_STATES = [
        (0, "Calm (glassy)"),
        (1, "Calm (rippled)"),
        (2, "Smooth"),
        (3, "Slight"),
        (4, "Moderate"),
        (5, "Rough"),
        (6, "Very rough"),
        (7, "High"),
        (8, "Very high"),
        (9, "Phenomenal"),
    ]

    temperature = models.FloatField()
    wind_speed = models.FloatField(validators=[MinValueValidator(0)])
    wind_direction = models.CharField(max_length=2, choices=WIND_DIRECTIONS)
    waterway_state = models.IntegerField(choices=WATER_STATES)


class MaintenanceLog(LogEntry):
    equipment = models.CharField(max_length=200)
    work_done = models.TextField(default="Some work was done", blank=True)
    hours_worked = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    minutes_worked = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    next_maintenance = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.notes:
            self.notes = self.notes.capitalize()
        super().save(*args, **kwargs)
