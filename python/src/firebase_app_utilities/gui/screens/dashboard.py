from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from ...core.project import FirebaseProject
from ..models import AnalyticsDashboardConfig
from ..tasks import TaskHost
from ..widgets import ActivityChart, MetricCard


class DashboardScreen(QWidget, TaskHost):
    PERIODS = (("Today", 1), ("7 days", 7), ("30 days", 30), ("90 days", 90), ("All cached", None))

    def __init__(self, project: FirebaseProject, config: AnalyticsDashboardConfig, parent: QWidget | None = None):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self.config = config
        self.cards: dict[str, MetricCard] = {}
        self._build()
        self.load_local()

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
        self.period.currentIndexChanged.connect(self.load_local)
        header.addWidget(self.period)

        self.sync_button = QPushButton("Sync new events")
        self.sync_button.setObjectName("PrimaryButton")
        self.sync_button.clicked.connect(self.sync)
        header.addWidget(self.sync_button)
        layout.addLayout(header)

        self.status = QLabel("Local cache only · no Firebase request has been made")
        self.status.setObjectName("Muted")
        layout.addWidget(self.status)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        for index, event in enumerate(self.config.events):
            card = MetricCard(event.title, hint=event.description or event.name)
            self.cards[event.name] = card
            grid.addWidget(card, index // 3, index % 3)
        layout.addLayout(grid)

        self.activity = ActivityChart()
        layout.addWidget(self.activity)
        layout.addStretch()

    def load_local(self) -> None:
        days = self.period.currentData()
        for event in self.config.events:
            self.cards[event.name].set_value(
                self.project.analytics.local_count(event_name=event.name, days=days)
            )
        self.activity.set_data(self.project.analytics.local_activity_by_day(days=days))

        sync_times = [
            self.project.analytics.last_sync(event_name=event.name, days=days)
            for event in self.config.events
        ]
        sync_times = [value for value in sync_times if value is not None]
        if sync_times:
            latest = max(sync_times)
            self.status.setText(f"Showing cached data · last sync {self._format_datetime(latest)}")
        else:
            self.status.setText("Local cache only · click Sync new events when you want to query Firebase")

    def sync(self) -> None:
        days = self.period.currentData()
        self.sync_button.setEnabled(False)
        self.sync_button.setText("Syncing…")
        self.status.setText("Fetching only events newer than the local cache…")

        def load() -> dict[str, Any]:
            fetched = 0
            more = False
            for event in self.config.events:
                result = self.project.analytics.sync_events(
                    event_name=event.name,
                    days=days,
                    limit=self.config.sync_limit,
                )
                fetched += int(result["fetched"])
                more = more or bool(result["has_more"])
            return {"fetched": fetched, "has_more": more}

        self.run_task(load, on_result=self._sync_finished, on_error=self._show_error, on_finished=self._finish)

    def _sync_finished(self, result: dict[str, Any]) -> None:
        self.load_local()
        suffix = " More data is available; sync again to continue." if result.get("has_more") else ""
        self.status.setText(f"Synced {result.get('fetched', 0)} new events.{suffix}")

    def _finish(self) -> None:
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Sync new events")

    def _show_error(self, error: Exception) -> None:
        self.status.setText("Sync failed; cached data was kept unchanged")
        QMessageBox.critical(self, "FirebaseAppUtilities", str(error))

    def _select_period(self, days: int | None) -> None:
        for index in range(self.period.count()):
            if self.period.itemData(index) == days:
                self.period.setCurrentIndex(index)
                return

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.astimezone().strftime("%Y-%m-%d %H:%M")
