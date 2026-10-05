from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PropertyKind = Literal["string", "int", "double", "bool"]
InsightKind = Literal["top_values", "bool_distribution", "average", "count"]


@dataclass(frozen=True, slots=True)
class AnalyticsProperty:
    key: str
    title: str
    kind: PropertyKind = "string"
    filterable: bool = True


@dataclass(frozen=True, slots=True)
class AnalyticsInsight:
    title: str
    kind: InsightKind
    property_key: str | None = None
    limit: int = 8

    @classmethod
    def top_values(
        cls,
        title: str,
        property_key: str,
        *,
        limit: int = 8,
    ) -> "AnalyticsInsight":
        return cls(title=title, kind="top_values", property_key=property_key, limit=limit)

    @classmethod
    def bool_distribution(cls, title: str, property_key: str) -> "AnalyticsInsight":
        return cls(title=title, kind="bool_distribution", property_key=property_key)

    @classmethod
    def average(cls, title: str, property_key: str) -> "AnalyticsInsight":
        return cls(title=title, kind="average", property_key=property_key)


@dataclass(frozen=True, slots=True)
class AnalyticsEventDefinition:
    name: str
    title: str
    description: str = ""
    properties: tuple[AnalyticsProperty, ...] = ()
    insights: tuple[AnalyticsInsight, ...] = ()


@dataclass(frozen=True, slots=True)
class AnalyticsDashboardConfig:
    title: str = "Analytics"
    subtitle: str = "Product activity and event intelligence"
    events: tuple[AnalyticsEventDefinition, ...] = ()
    period_days: int | None = 30
    sync_limit: int = 1000
    recent_limit: int = 50

    @property
    def event_labels(self) -> dict[str, str]:
        return {event.name: event.title for event in self.events}


@dataclass(frozen=True, slots=True)
class SupportConfig:
    collection: str = "messages"
    timestamp_field: str = "createdAt"
    title: str = "Support"
    subtitle: str = "Customer support messages"
    categories: dict[str, str] = field(default_factory=dict)
    period_days: int | None = 30
    sync_limit: int = 500
    visible_limit: int = 100
