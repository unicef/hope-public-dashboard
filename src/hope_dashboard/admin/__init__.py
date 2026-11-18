from django.contrib import admin

from .constance import ConstanceConfigAdmin  # noqa: F401

admin.site.site_header = "HOPE Public Dashboard"
admin.site.site_title = "HOPE Public Dashboard"
admin.site.index_title = "Configuration"

__all__ = [
    "ConstanceConfigAdmin",
]
