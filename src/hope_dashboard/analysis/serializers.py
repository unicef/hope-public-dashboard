from rest_framework import serializers  # type: ignore[import-untyped]

from .models import DemographicAggregate, FinancialAggregate


class FinancialAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = FinancialAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "program_type",
            "total_usd",
            "total_qty",
            "payment_count",
        ]


class DemographicAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DemographicAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "program_type",
            "total_beneficiaries",
            "total_children",
            "total_pwd",
            "total_households",
        ]
