import datetime as dt

import pytest

from hope_dashboard.analysis.models import DemographicAggregate, FinancialAggregate, TimeGrain

pytestmark = [pytest.mark.django_db, pytest.mark.selenium]


def test_landing_page_renders_all_charts(browser):
    FinancialAggregate.objects.create(
        date=dt.date(2024, 1, 1),
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="sector",
        dimension_value="education",
        total_usd=1000,
        payment_count=10,
    )
    FinancialAggregate.objects.create(
        date=dt.date(2024, 1, 1),
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="delivery_type",
        dimension_value="mobile_money",
        total_usd=1000,
        payment_count=10,
    )
    DemographicAggregate.objects.create(
        date=dt.date(2024, 1, 1),
        time_grain=TimeGrain.MONTHLY,
        country_slug="kenya",
        dimension_type="sector",
        dimension_value="education",
        total_beneficiaries=100,
        total_children=50,
        total_households=20,
    )

    browser.open("/")
    browser.wait_for_text("Explore the evidence", timeout=15)

    for selector in [
        "#world-map-chart canvas",
        "#sector-chart canvas",
        "#trends-chart canvas",
        "#mechanism-chart canvas",
    ]:
        browser.wait_for_element_visible(selector, timeout=20)

    assert browser.get_text("#kpi-children") == "50"
    assert browser.get_text("#kpi-families") == "20"
    assert browser.get_text("#kpi-individuals") == "100"
