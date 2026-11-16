from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny

from ..models import DemographicAggregate, FinancialAggregate, TimeGrain
from ..serializers import DemographicAggregateSerializer, FinancialAggregateSerializer

if TYPE_CHECKING:
    from django.db import models
    from rest_framework.request import Request
    from rest_framework.response import Response


def _apply_common_filters(queryset: models.QuerySet, params: Any, dash_type: str | None) -> models.QuerySet:
    time_grain = params.get("time_grain")
    if not time_grain or time_grain not in TimeGrain.values:
        time_grain = TimeGrain.MONTHLY if dash_type == "demographic" else TimeGrain.DAILY
    queryset = queryset.filter(time_grain=time_grain)

    year = params.get("year")
    if year:
        queryset = queryset.filter(date__year=int(year))

    dimension_type = params.get("dimension_type")
    if dimension_type:
        queryset = queryset.filter(dimension_type=dimension_type)

    program_type = params.get("program_type")
    if program_type:
        queryset = queryset.filter(program_type__iexact=program_type)

    country_slug = params.get("country_slug")
    if country_slug:
        queryset = queryset.filter(country_slug=country_slug)

    date_from = params.get("date_from")
    date_to = params.get("date_to")
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


@method_decorator(cache_page(60 * 60 * 6), name="dispatch")
class AggregateListView(generics.ListAPIView):  # type: ignore[misc]
    """Public API endpoint used by the public landing page.

    The landing page loads the whole aggregate table client-side (and filters
    there), so this endpoint must return a plain JSON array rather than DRF's
    default paginated envelope.
    """

    permission_classes = [AllowAny]
    pagination_class = None

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        if self.request.query_params.get("dashboard") == "demographic":
            return DemographicAggregateSerializer
        return FinancialAggregateSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                description="Filter by year (YYYY)",
                required=False,
                type=int,
                examples=[OpenApiExample("2024", value=2024)],
            ),
            OpenApiParameter(
                name="dimension_type",
                description="Filter by dimension type (sector, program, delivery_type, etc.)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Sector", value="sector"),
                    OpenApiExample("Program", value="program"),
                ],
            ),
            OpenApiParameter(
                name="country_slug",
                description="Filter by country slug",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="program_type",
                description="Filter by programme cohort (STANDARD or SOCIAL)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Social workers", value="SOCIAL"),
                    OpenApiExample("Standard programmes", value="STANDARD"),
                ],
            ),
            OpenApiParameter(
                name="date_from",
                description="Filter by start date (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date_to",
                description="Filter by end date (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="dashboard",
                description="Filter by dashboard type (financial or demographic)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Financial", value="financial"),
                    OpenApiExample("Demographic", value="demographic"),
                ],
            ),
        ],
        description="List Aggregate records with optional filtering",
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> models.QuerySet:  # type: ignore[type-arg]
        dash_type = self.request.query_params.get("dashboard")

        if dash_type == "demographic":
            queryset = DemographicAggregate.objects.all()
        else:
            queryset = FinancialAggregate.objects.exclude(dimension_type="currency")

        return _apply_common_filters(queryset, self.request.query_params, dash_type)
