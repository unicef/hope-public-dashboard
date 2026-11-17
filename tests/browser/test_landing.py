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
    FinancialAggregate.objects.create(
        date=dt.date(2024, 1, 1),
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="sector",
        dimension_value="SOCIAL_POLICY",
        total_usd=500,
        payment_count=5,
    )
    FinancialAggregate.objects.create(
        date=dt.date(2024, 1, 1),
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="delivery_type",
        dimension_value="TRANSFER_TO_ACCOUNT",
        total_usd=500,
        payment_count=5,
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

    assert "Noto Sans" in browser.execute_script("return getComputedStyle(document.body).fontFamily")

    assert browser.execute_script("return window.HopeChart.formatLabel('SOCIAL_POLICY')") == "Social Policy"
    assert browser.execute_script("return window.HopeChart.formatLabel('MULTI_PURPOSE')") == "Multi-Purpose Cash"

    sector_legend = browser.execute_script(
        """
        const option = echarts.getInstanceByDom(document.getElementById('sector-chart')).getOption();
        return option.series[0].data.map(item => item.name);
        """
    )
    assert "Social Policy" in sector_legend

    mechanism_legend = browser.execute_script(
        """
        const option = echarts.getInstanceByDom(document.getElementById('mechanism-chart')).getOption();
        return option.series[0].data.map(item => item.name);
        """
    )
    assert "Transfer to Account" in mechanism_legend

    scale_limit = browser.execute_script(
        """
        const option = echarts.getInstanceByDom(document.getElementById('world-map-chart')).getOption();
        const value = option.series[0].scaleLimit.min;
        return Array.isArray(value) ? value[0] : value;
        """
    )
    assert scale_limit == 1

    color_range = browser.execute_script(
        """
        const option = echarts.getInstanceByDom(document.getElementById('world-map-chart')).getOption();
        const value = option.visualMap[0].inRange.color;
        return Array.isArray(value[0]) ? value[0] : value;
        """
    )
    assert color_range == ["#9ADBE8", "#00AEEF", "#0047BB"]

    for _ in range(10):
        browser.click("#map-zoom-out")

    zoom = browser.execute_script(
        """
        const option = echarts.getInstanceByDom(document.getElementById('world-map-chart')).getOption();
        const value = option.series[0].zoom;
        return Array.isArray(value) ? value[0] : value;
        """
    )
    assert zoom >= 1
