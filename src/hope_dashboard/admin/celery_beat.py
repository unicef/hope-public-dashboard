# mypy: ignore-errors

from django.contrib import admin
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule

admin.site.unregister([PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule])


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin):
    pass


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(BaseCrontabScheduleAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(BaseClockedScheduleAdmin):
    pass
