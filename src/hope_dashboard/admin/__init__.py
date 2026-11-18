from django.contrib import admin

from .celery_beat import (  # noqa: F401
    ClockedScheduleAdmin,
    CrontabScheduleAdmin,
    IntervalScheduleAdmin,
    PeriodicTaskAdmin,
    SolarScheduleAdmin,
)
from .constance import ConstanceConfigAdmin  # noqa: F401
from .user import UserAdmin  # noqa: F401

admin.site.site_header = "HOPE Public Dashboard"
admin.site.site_title = "HOPE Public Dashboard"
admin.site.index_title = "Administration"

__all__ = [
    "ClockedScheduleAdmin",
    "ConstanceConfigAdmin",
    "CrontabScheduleAdmin",
    "IntervalScheduleAdmin",
    "PeriodicTaskAdmin",
    "SolarScheduleAdmin",
    "UserAdmin",
]
