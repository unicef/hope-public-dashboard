from typing import Any

from .mail import MAILJET_API_KEY, MAILJET_SECRET_KEY

from .. import env

CONSTANCE_ADDITIONAL_FIELDS = {
    "write_only_input": [
        "django.forms.fields.CharField",
        {
            "required": False,
            "widget": "hope_dashboard.utils.constance.WriteOnlyInput",
        },
    ],
    "token": [
        "django.forms.fields.CharField",
        {
            "required": False,
            "widget": "hope_dashboard.utils.constance.WriteOnlyInput",
        },
    ],
    "group_select": [
        "hope_dashboard.utils.constance.GroupSelect",
        {"initial": None},
    ],
}

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_CACHE_BACKEND = env("CONSTANCE_DATABASE_CACHE_BACKEND")
CONSTANCE_CONFIG: dict[str, tuple[Any, str, Any]] = {
    "NEW_USER_DEFAULT_GROUP": (None, "Group to assign to any new user", "group_select"),
    "LOGIN_LOCAL": (True, "Enable local accounts login", bool),
    "LOGIN_SSO": (True, "Enable SSO logon", bool),
    "MAILJET_API_KEY": (MAILJET_API_KEY, "Mailjet API key", str),
    "MAILJET_SECRET_KEY": (MAILJET_SECRET_KEY, "Mailjet secret key", "write_only_input"),
    "HOPE_COUNTRY_REPORT_API_URL": (
        "https://reporting-hope-dev.unitst.org/api/",
        "Country Report API URL",
        str,
    ),
    "HOPE_COUNTRY_REPORT_API_TOKEN": (
        "8ac98d372760c5db87b73e1c283dcb1bc8c4f0e6",
        "Country Report API Token",
        "token",
    ),
    "HOPE_FINANCIAL_REPORT_QUERY_ID": (
        6,
        "Query ID for Financial Aggregate Dataset",
        int,
    ),
    "HOPE_DEMOGRAPHIC_REPORT_QUERY_ID": (
        7,
        "Query ID for Demographic Aggregate Dataset",
        int,
    ),
}
