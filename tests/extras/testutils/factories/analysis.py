import factory

from hope_dashboard.analysis.models import DemographicAggregate, FinancialAggregate, SyncDailyAggregatesJob

from .base import AutoRegisterModelFactory


class FinancialAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_decade")
    time_grain = "daily"
    country_slug = factory.Sequence(lambda n: f"country-{n}")
    dimension_type = "sector"
    dimension_value = factory.Sequence(lambda n: f"sector-{n}")
    total_usd = 1000
    total_qty = 10
    payment_count = 5

    class Meta:
        model = FinancialAggregate


class DemographicAggregateFactory(AutoRegisterModelFactory):
    date = factory.Faker("date_this_decade")
    time_grain = "monthly"
    country_slug = factory.Sequence(lambda n: f"country-{n}")
    dimension_type = "sector"
    dimension_value = factory.Sequence(lambda n: f"sector-{n}")
    total_beneficiaries = 100
    total_children = 50
    total_pwd = 5
    total_households = 20

    class Meta:
        model = DemographicAggregate


class SyncDailyAggregatesJobFactory(AutoRegisterModelFactory):
    description = factory.Sequence(lambda n: f"Sync job {n}")

    class Meta:
        model = SyncDailyAggregatesJob
