import pytest
from constance.test.pytest import override_config

pytestmark = pytest.mark.django_db


@override_config(HOPE_COUNTRY_REPORT_API_TOKEN="")
def test_sync_requires_report_token() -> None:
    from hope_dashboard.analysis.tasks import sync_daily_aggregates

    with pytest.raises(ValueError, match="HOPE_COUNTRY_REPORT_API_TOKEN"):
        sync_daily_aggregates.apply().get()
