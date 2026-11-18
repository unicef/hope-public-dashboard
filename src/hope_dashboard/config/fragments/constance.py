from typing import Any

from .. import env

CONSTANCE_ADDITIONAL_FIELDS = {
    "token": [
        "django.forms.fields.CharField",
        {
            "required": False,
            "widget": "hope_dashboard.utils.constance.WriteOnlyInput",
        },
    ],
}

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_CACHE_BACKEND = env("CONSTANCE_DATABASE_CACHE_BACKEND")
CONSTANCE_CONFIG: dict[str, tuple[Any, str, Any]] = {
    "HOPE_COUNTRY_REPORT_API_URL": (
        "https://reporting-hope-trn.unitst.org/api/offices/global/",
        "Country Report API URL",
        str,
    ),
    "HOPE_COUNTRY_REPORT_API_TOKEN": (
        "8ac98d372760c5db87b73e1c283dcb1bc8c4f0e6",
        "Country Report API Token",
        "token",
    ),
    "HOPE_FINANCIAL_REPORT_QUERY_ID": (
        101,
        "Query ID for Financial Aggregate Dataset",
        int,
    ),
    "HOPE_DEMOGRAPHIC_REPORT_QUERY_ID": (
        132,
        "Query ID for Demographic Aggregate Dataset",
        int,
    ),
}
