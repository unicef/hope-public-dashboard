import datetime as dt
from typing import Any

from django.db.models import Max, Sum
from django.http import HttpRequest, HttpResponse
from django.utils.formats import date_format
from django.views import View
from django.views.generic import TemplateView

from hope_dashboard.analysis.models import DemographicAggregate, FinancialAggregate, ProgramType

from ._common import MediaMixin

BILLION = 1_000_000_000
MILLION = 1_000_000
THOUSAND = 1_000


def format_large_number(num: float) -> str:
    if num >= BILLION:
        val = num / BILLION
        return f"{val:.1f}B".replace(".0B", "B")
    if num >= MILLION:
        val = num / MILLION
        return f"{val:.1f}M".replace(".0M", "M")
    if num >= THOUSAND:
        val = num / THOUSAND
        return f"{val:.1f}K".replace(".0K", "K")
    return str(int(num))


class LandingView(TemplateView):
    template_name = "pages/landing.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Calculate Total Cash Disbursed (filtering by sector to avoid double counting)
        total_usd = (
            FinancialAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_usd"))["total"] or 0
        )

        # Head-count demographics describe standard programmes only; for social-worker
        # programmes one record is one worker, so they are reported separately below.
        standard_demographics = DemographicAggregate.objects.filter(
            dimension_type="sector", program_type=ProgramType.STANDARD
        )

        # Calculate Total Individuals Reached
        total_beneficiaries = standard_demographics.aggregate(total=Sum("total_beneficiaries"))["total"] or 0

        # Calculate Total Children Reached
        total_children = standard_demographics.aggregate(total=Sum("total_children"))["total"] or 0

        # Calculate Total Households Reached
        total_households = standard_demographics.aggregate(total=Sum("total_households"))["total"] or 0

        # Calculate Social Workers Assisted. In social-worker programmes each household
        # record represents one worker, so `total_beneficiaries` is the workforce count.
        total_social_workers = (
            DemographicAggregate.objects.filter(dimension_type="sector", program_type=ProgramType.SOCIAL).aggregate(
                total=Sum("total_beneficiaries")
            )["total"]
            or 0
        )
        if not total_social_workers:
            # Transitional: before the feed emitted `program_type` as a column, the cohort was
            # exposed as its own dimension. Drop this fallback once the re-sync has run.
            total_social_workers = (
                DemographicAggregate.objects.filter(
                    dimension_type="program_type", dimension_value=ProgramType.SOCIAL
                ).aggregate(total=Sum("total_beneficiaries"))["total"]
                or 0
            )

        # HOPE at a glance sidebar statistics
        # Unique countries across all aggregates
        countries_set = set(FinancialAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(DemographicAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.discard("")
        countries_set.discard(None)
        total_countries_glance = len(countries_set)

        # Unique programs count from FinancialAggregate (where dimension_type is program)
        total_programs_glance = (
            FinancialAggregate.objects.filter(dimension_type="program").values("dimension_value").distinct().count()
        )

        # Data source name
        total_sources_glance = "HOPE Database"

        # Find latest data date
        latest_date_f = FinancialAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_d = DemographicAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        dates = [d for d in [latest_date_f, latest_date_d] if d]
        latest_data_date = max(dates) if dates else None

        if latest_data_date:
            latest_data_str = date_format(latest_data_date, "F Y")
            latest_data_exact = date_format(latest_data_date, "d M Y")
        else:
            latest_data_str = date_format(dt.date(2026, 5, 1), "F Y")
            latest_data_exact = latest_data_str

        total_payments = (
            FinancialAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("payment_count"))["total"]
            or 0
        )
        context["total_cash_disbursed"] = format_large_number(total_usd)
        context["total_payments"] = format_large_number(total_payments)
        context["average_transfer"] = format_large_number(total_usd / total_payments) if total_payments else "0"
        context["total_individuals_reached"] = format_large_number(total_beneficiaries)
        context["total_children"] = format_large_number(total_children)
        context["total_households"] = format_large_number(total_households)
        context["total_social_workers"] = format_large_number(total_social_workers)
        context["total_countries_glance"] = total_countries_glance or 170
        context["total_programs_glance"] = total_programs_glance or 450
        context["total_sources_glance"] = total_sources_glance
        context["latest_data_str"] = latest_data_str
        context["latest_data_exact"] = latest_data_exact

        return context


class HomeView(LandingView):
    """Backwards-compatible alias for the public landing page."""


class HealthCheckView(MediaMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("Ok")
