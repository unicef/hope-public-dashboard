import datetime as dt
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.urls import reverse

from hope_dashboard.analysis.models import DemographicAggregate, FinancialAggregate, TimeGrain

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def clear_api_cache():
    cache.clear()
    yield
    cache.clear()


def _financial(**kwargs):
    defaults = {
        "date": dt.date(2024, 1, 1),
        "time_grain": TimeGrain.DAILY,
        "country_slug": "kenya",
        "dimension_type": "sector",
        "dimension_value": "education",
        "total_usd": 1000,
        "payment_count": 10,
    }
    return FinancialAggregate.objects.create(**{**defaults, **kwargs})


def _demographic(**kwargs):
    defaults = {
        "date": dt.date(2024, 1, 1),
        "time_grain": TimeGrain.MONTHLY,
        "country_slug": "kenya",
        "dimension_type": "sector",
        "dimension_value": "education",
        "total_beneficiaries": 100,
        "total_children": 50,
        "total_households": 20,
    }
    return DemographicAggregate.objects.create(**{**defaults, **kwargs})


def test_public_landing_page_is_open(client):
    _financial()
    _demographic()
    response = client.get("/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Explore the evidence" in content
    assert "Cash-based Assistance" in content
    assert "/login/" not in content
    assert "Sign In" not in content
    assert response.context["total_cash_disbursed"] == "1K"
    assert response.context["total_payments"] == "10"
    assert response.context["total_individuals_reached"] == "100"
    assert response.context["total_children"] == "50"
    assert response.context["total_households"] == "20"
    assert response.context["total_countries_glance"] == 1


def test_landing_includes_public_charts_data_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "api/analysis/daily-aggregates" in response.content.decode()


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("es", "Explorar la evidencia"),
        ("fr", "Explorer les données"),
        ("ar", "استكشاف الأدلة"),
        ("ru", "Изучить данные"),
        ("zh-hans", "探索数据"),
    ],
)
def test_language_switch_renders_landing_translations(client, language, expected):
    response = client.post(reverse("set_language"), {"language": language, "next": "/"})
    assert response.status_code == 302

    response = client.get("/")
    content = response.content.decode()

    assert response.status_code == 200
    assert expected in content
    assert f'lang="{language}"' in content
    if language == "ar":
        assert 'dir="rtl"' in content


def test_public_aggregate_api_returns_plain_array(client):
    _financial()
    _demographic()

    response = client.get(reverse("analysis_api:daily-aggregates-list"), {"dashboard": "financial"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["country_slug"] == "kenya"
    assert data[0]["dimension_type"] == "sector"


def test_public_aggregate_api_demographic_monthly(client):
    _demographic()

    response = client.get(
        reverse("analysis_api:daily-aggregates-list"),
        {"dashboard": "demographic", "time_grain": "monthly"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["total_children"] == 50
    assert data[0]["program_type"] == "STANDARD"


def test_public_page_sets_content_security_policy(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "default-src" in response["Content-Security-Policy"]
    assert response["X-Frame-Options"] == "SAMEORIGIN"


def test_public_css_contains_responsive_layout_utilities():
    css_path = finders.find("css/public.css")
    assert css_path
    css = Path(css_path).read_text()
    for selector in [
        "lg\\:grid-cols-12",
        "lg\\:col-span-8",
        "lg\\:col-span-4",
        "sm\\:grid-cols-2",
        "xl\\:grid-cols-12",
    ]:
        assert selector in css, selector


def test_public_assets_are_available():
    for path in [
        "css/public.css",
        "fonts/NotoSans-Regular.woff2",
        "fonts/NotoSans-Bold.woff2",
        "fonts/NotoSansArabic-Regular.woff2",
        "fonts/NotoSansSC-Regular.woff2",
        "js/echarts.min.js",
        "js/d3.min.js",
        "js/topojson-client.min.js",
        "js/macarons.js",
        "js/chart_helpers.js",
        "js/public_theme.js",
        "data/world.json",
        "images/background.png",
        "images/logo-white-trimmed.png",
    ]:
        assert finders.find(path), path


def test_constance_contains_data_fetch_settings():
    from constance import config

    for key in [
        "HOPE_COUNTRY_REPORT_API_URL",
        "HOPE_COUNTRY_REPORT_API_TOKEN",
        "HOPE_FINANCIAL_REPORT_QUERY_ID",
        "HOPE_DEMOGRAPHIC_REPORT_QUERY_ID",
    ]:
        assert hasattr(config, key), key


def test_celery_aggregate_tasks_are_registered():
    from hope_dashboard.analysis.models import SyncDailyAggregatesJob
    from hope_dashboard.config.celery import app

    for task_name in [
        "hope_dashboard.analysis.tasks.sync_daily_aggregates",
        "hope_dashboard.analysis.tasks.save_aggregates",
        "hope_dashboard.analysis.tasks.schedule_sync_daily_aggregates",
        "hope_dashboard.analysis.tasks.clear_daily_aggregates",
    ]:
        assert task_name in app.tasks, task_name

    assert SyncDailyAggregatesJob.celery_task_name in app.tasks


def test_save_aggregates_persists_synced_rows():
    from hope_dashboard.analysis.tasks import save_aggregates

    rows = [
        {
            "date": "2024-01-01",
            "time_grain": "daily",
            "country_slug": "kenya",
            "dimension_type": "sector",
            "dimension_value": "health",
            "program_type": "SOCIAL",
            "total_usd": 100,
            "total_qty": 10,
            "payment_count": 5,
        },
        {"country_slug": "missing_date"},
    ]

    save_aggregates(rows, 2024, "FinancialAggregate", ["total_usd", "total_qty", "payment_count"])

    record = FinancialAggregate.objects.get()
    assert record.country_slug == "kenya"
    assert record.program_type == "SOCIAL"
    assert record.total_usd == 100


def test_admin_requires_login_and_exposes_data_configuration(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]

    from testutils.factories import SuperUserFactory

    admin_user = SuperUserFactory(username="admin-landing")
    client.force_login(admin_user)

    response = client.get("/admin/")
    assert response.status_code == 200

    response = client.get("/admin/constance/config/")
    assert response.status_code == 200
    assert "HOPE_COUNTRY_REPORT_API_URL" in response.content.decode()

    response = client.get("/admin/analysis/syncdailyaggregatesjob/")
    assert response.status_code == 200
