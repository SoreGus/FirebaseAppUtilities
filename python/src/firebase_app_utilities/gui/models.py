from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MetricKind = Literal[
    "event_count",
    "total_events",
    "unique_users",
    "unique_sessions",
]


@dataclass(frozen=True, slots=True)
class AnalyticsMetric:
    title: str
    kind: MetricKind = "event_count"
    event_name: str | None = None
    hint: str | None = None

    @classmethod
    def event(
        cls,
        title: str,
        event_name: str,
        *,
        hint: str | None = None,
    ) -> "AnalyticsMetric":
        return cls(
            title=title,
            kind="event_count",
            event_name=event_name,
            hint=hint,
        )


@dataclass(frozen=True, slots=True)
class PropertyRanking:
    title: str
    property_key: str
    event_name: str | None = None
    limit: int = 8


@dataclass(frozen=True, slots=True)
class AnalyticsDashboardConfig:
    title: str = "Analytics"
    subtitle: str = "Product activity and event intelligence"
    metrics: tuple[AnalyticsMetric, ...] = (
        AnalyticsMetric(
            title="Events",
            kind="total_events",
        ),
        AnalyticsMetric(
            title="Sessions",
            kind="unique_sessions",
        ),
        AnalyticsMetric(
            title="Users",
            kind="unique_users",
        ),
    )
    rankings: tuple[PropertyRanking, ...] = ()
    recent_events_limit: int = 40
    aggregation_limit: int = 5000
    period_days: int | None = 30
    event_labels: dict[str, str] = field(default_factory=dict)
