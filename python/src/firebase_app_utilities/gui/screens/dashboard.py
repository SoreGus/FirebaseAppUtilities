from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..models import AnalyticsDashboardConfig, AnalyticsMetric, PropertyRanking
from ..tasks import TaskHost
from ..widgets import ActivityChart, EventTable, MetricCard, RankingCard


class DashboardScreen(QWidget, TaskHost):
    PERIODS: tuple[tuple[str, int | None], ...] = (
        ("24 hours", 1),
        ("7 days", 7),
        ("30 days", 30),
        ("90 days", 90),
        ("All time", None),
    )

    def __init__(
        self,
        project: FirebaseProject,
        config: AnalyticsDashboardConfig,
        parent: QWidget | None = None,
    ):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self.config = config
        self.metric_cards: list[tuple[AnalyticsMetric, MetricCard]] = []
        self.ranking_cards: list[tuple[PropertyRanking, RankingCard]] = []
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        title = QLabel(self.config.title)
        title.setObjectName("PageTitle")
        subtitle = QLabel(self.config.subtitle)
        subtitle.setObjectName("PageSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        self.period = QComboBox()
        for label, value in self.PERIODS:
            self.period.addItem(label, value)
        self._select_period(self.config.period_days)
        self.period.currentIndexChanged.connect(self.refresh)
        header.addWidget(self.period)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("PrimaryButton")
        self.refresh_button.clicked.connect(self.refresh)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        self.status = QLabel(
            f"{self.project.project_id} · {self.project.environment} · connected"
        )
        self.status.setObjectName("Success")
        layout.addWidget(self.status)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(12)
        metrics.setVerticalSpacing(12)

        for index, metric in enumerate(self.config.metrics):
            card = MetricCard(metric.title, hint=metric.hint)
            self.metric_cards.append((metric, card))
            metrics.addWidget(card, 0, index)
            metrics.setColumnStretch(index, 1)

        layout.addLayout(metrics)

        analytics_row = QGridLayout()
        analytics_row.setHorizontalSpacing(14)
        analytics_row.setVerticalSpacing(14)

        self.activity = ActivityChart()
        analytics_row.addWidget(self.activity, 0, 0, 1, 2)
        analytics_row.setColumnStretch(0, 2)
        analytics_row.setColumnStretch(1, 2)

        for index, ranking in enumerate(self.config.rankings):
            card = RankingCard(ranking.title)
            self.ranking_cards.append((ranking, card))
            row = index // 2 + 1
            column = index % 2
            analytics_row.addWidget(card, row, column)

        layout.addLayout(analytics_row)

        events_panel = QFrame()
        events_panel.setObjectName("Panel")
        events_layout = QVBoxLayout(events_panel)
        events_layout.setContentsMargins(16, 15, 16, 16)
        events_layout.setSpacing(10)

        recent_title = QLabel("Recent events")
        recent_title.setObjectName("SectionTitle")
        events_layout.addWidget(recent_title)

        self.events = EventTable()
        self.events.setMinimumHeight(270)
        events_layout.addWidget(self.events)
        layout.addWidget(events_panel)
        layout.addStretch()

    def refresh(self) -> None:
        days = self.period.currentData()
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading…")
        self.status.setText("Refreshing analytics…")

        def load() -> dict[str, Any]:
            snapshot = self.project.analytics.dashboard_snapshot(
                days=days,
                recent_limit=self.config.recent_events_limit,
                aggregation_limit=self.config.aggregation_limit,
            )
            snapshot["rankings"] = [
                self.project.analytics.property_counts(
                    ranking.property_key,
                    event_name=ranking.event_name,
                    days=days,
                    limit=self.config.aggregation_limit,
                    top=ranking.limit,
                )
                for ranking in self.config.rankings
            ]
            return snapshot

        self.run_task(
            load,
            on_result=self._apply_snapshot,
            on_error=self._show_error,
            on_finished=self._finish_refresh,
        )

    def _apply_snapshot(self, snapshot: dict[str, Any]) -> None:
        overview = snapshot["overview"]
        event_counts = overview.get("events", {})

        for metric, card in self.metric_cards:
            if metric.kind == "total_events":
                value = overview.get("total_events", 0)
            elif metric.kind == "unique_users":
                value = overview.get("unique_users", 0)
            elif metric.kind == "unique_sessions":
                value = overview.get("unique_sessions", 0)
            else:
                value = event_counts.get(metric.event_name or "", 0)
            card.set_value(value)

        self.activity.set_data(snapshot.get("activity", []))

        ranking_values = snapshot.get("rankings", [])
        for index, (_, card) in enumerate(self.ranking_cards):
            values = ranking_values[index] if index < len(ranking_values) else {}
            card.set_values(values)

        self.events.set_events(
            snapshot.get("recent_events", []),
            self.config.event_labels,
        )
        self.status.setText(
            f"{self.project.project_id} · {self.project.environment} · live data"
        )

    def _finish_refresh(self) -> None:
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")

    def _show_error(self, error: Exception) -> None:
        self.status.setText("Analytics refresh failed")
        QMessageBox.critical(self, "FirebaseAppUtilities", str(error))

    def _select_period(self, days: int | None) -> None:
        for index in range(self.period.count()):
            if self.period.itemData(index) == days:
                self.period.setCurrentIndex(index)
                return
