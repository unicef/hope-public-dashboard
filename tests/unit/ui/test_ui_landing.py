import datetime as dt
import re
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
    assert "Children Reached" in content
    assert "Cash Delivered (USD)" in content
    assert "Payments delivered" in content
    assert "Average transfer" in content
    assert "Disclaimer: All figures shown are indicative only and may vary due to rounding" in content
    assert "HOPE reach" not in content
    assert "Frontline workforce assisted" not in content
    assert "Play years" in content
    assert "Data protection" in content
    assert "Methodology" in content
    assert "https://www.unicef.org/documents/policy-personal-data-protection" in content
    assert content.count("unicef-logo-white-en.png") == 1
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
    ("language", "expected", "logo", "expected_strings"),
    [
        (
            "es",
            "Explorar la evidencia",
            "unicef-logo-white-es.png",
            [
                "Política social",
                "Transferencia a cuenta",
                "Efectivo por ventanilla",
                "Tarjeta de cajero automático",
                "Aviso legal: Todas las cifras mostradas son meramente indicativas",
                "1 de enero de 2024",
            ],
        ),
        (
            "fr",
            "Explorer les données",
            "unicef-logo-white-fr.png",
            [
                "Politique sociale",
                "Virement sur compte",
                "Retrait d\\u0027espèces au guichet",
                "Carte bancaire (GAB)",
                "Avertissement : tous les chiffres indiqués le sont à titre indicatif",
                "Transfert moyen",
                "1 janvier 2024",
            ],
        ),
        (
            "ar",
            "استكشاف الأدلة",
            "unicef-logo-white-ar.png",
            [
                "السياسات الاجتماعية",
                "تحويل إلى حساب",
                "صرف نقدي عبر منافذ الخدمة",
                "بطاقة صراف آلي",
                "إخلاء مسؤولية: جميع الأرقام المعروضة استرشادية فقط",
            ],
        ),
        (
            "ru",
            "Изучить данные",
            "unicef-logo-white-ru.png",
            [
                "Социальная политика",
                "Перевод на счёт",
                "Наличные через кассу",
                "Банковская карта (банкомат)",
                "Примечание: все представленные данные носят ориентировочный характер",
            ],
        ),
        (
            "zh-hans",
            "探索数据",
            "unicef-logo-white-zh.png",
            [
                "社会政策",
                "账户转账",
                "柜台现金支取",
                "代金券",
                "ATM 卡",
                "免责声明：所示数据仅供参考，因四舍五入可能存在差异",
                "平均发放金额",
                "已发放笔数",
                "所选年份各国覆盖情况",
                "统计方法",
                "2024年1月1日",
            ],
        ),
    ],
)
def test_language_switch_renders_landing_translations(client, language, expected, logo, expected_strings):
    _financial()
    _demographic()
    response = client.post(reverse("set_language"), {"language": language, "next": "/"})
    assert response.status_code == 302

    response = client.get("/")
    content = response.content.decode()

    assert response.status_code == 200
    assert expected in content
    for expected_str in expected_strings:
        assert expected_str in content, f"Missing {expected_str!r} in {language}"
    assert logo in content
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


def test_content_security_policy_does_not_allow_cdns(settings):
    directives = settings.CONTENT_SECURITY_POLICY["DIRECTIVES"]
    sources = [source for values in directives.values() for source in values]

    assert not any("cdn" in source or "unpkg" in source or "jsdelivr" in source for source in sources)


@pytest.mark.parametrize("url", ["/", reverse("ui:login")])
def test_public_pages_use_only_local_assets(client, url):
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    script_sources = re.findall(r'<script[^>]+src="([^"]+)"', content)
    stylesheet_sources = re.findall(r'<link[^>]+href="([^"]+)"', content)

    assert script_sources
    assert all(source.startswith("/") for source in script_sources), script_sources
    assert all(source.startswith("/") for source in stylesheet_sources), stylesheet_sources


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
        "images/unicef-logo-white-en.png",
        "images/unicef-logo-white-fr.png",
        "images/unicef-logo-white-es.png",
        "images/unicef-logo-white-ar.png",
        "images/unicef-logo-white-ru.png",
        "images/unicef-logo-white-zh.png",
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


def test_constance_defaults_match_report_environment():
    from constance import config

    assert config.HOPE_COUNTRY_REPORT_API_URL == "https://reporting-hope-trn.unitst.org/api/offices/global/"
    assert config.HOPE_COUNTRY_REPORT_API_TOKEN == ""
    assert config.HOPE_FINANCIAL_REPORT_QUERY_ID == 101
    assert config.HOPE_DEMOGRAPHIC_REPORT_QUERY_ID == 132


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
    assert client.get("/admin/").status_code == 404

    response = client.get(reverse("admin:index"))
    assert response.status_code == 302
    assert reverse("admin:login") in response["Location"]

    from testutils.factories import SuperUserFactory

    admin_user = SuperUserFactory(username="admin-landing")
    client.force_login(admin_user)

    response = client.get(reverse("admin:index"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "HOPE Public Dashboard" in content
    assert "Constance" in content
    assert "Periodic Tasks" in content
    assert "Sync Daily Aggregates Jobs" in content
    assert "Financial aggregates" in content
    assert "Demographic aggregates" in content

    response = client.get(reverse("admin:constance_config_changelist"))
    assert response.status_code == 200
    assert "HOPE_COUNTRY_REPORT_API_URL" in response.content.decode()

    response = client.get(reverse("admin:django_celery_beat_periodictask_changelist"))
    assert response.status_code == 200

    response = client.get(reverse("admin:analysis_syncdailyaggregatesjob_changelist"))
    assert response.status_code == 200
