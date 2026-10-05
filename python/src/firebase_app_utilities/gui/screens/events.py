from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..models import AnalyticsDashboardConfig, AnalyticsEventDefinition
from ..tasks import TaskHost
from ..widgets import ActivityChart, MetricCard, RankingCard, format_timestamp


class EventsScreen(QWidget, TaskHost):
    PERIODS = (("Today", 1), ("7 days", 7), ("30 days", 30), ("90 days", 90), ("All cached", None))

    def __init__(self, project: FirebaseProject, config: AnalyticsDashboardConfig, parent: QWidget | None = None):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self.config = config
        self.current_event: AnalyticsEventDefinition | None = config.events[0] if config.events else None
        self.ranking_cards: list[tuple[Any, RankingCard]] = []
        self.filter_widgets: dict[str, tuple[Any, Any]] = {}
        self._build()
        self._select_event(0)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Analytics")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Choose an event type, then explicitly sync or query only what you need.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter, 1)

        left = QFrame()
        left.setObjectName("Panel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.addWidget(QLabel("Event types"))
        self.events_list = QListWidget()
        for event in self.config.events:
            item = QListWidgetItem(event.title)
            item.setData(Qt.ItemDataRole.UserRole, event.name)
            self.events_list.addItem(item)
        self.events_list.currentRowChanged.connect(self._select_event)
        left_layout.addWidget(self.events_list)
        splitter.addWidget(left)

        self.detail = QWidget()
        self.detail_layout = QVBoxLayout(self.detail)
        self.detail_layout.setContentsMargins(18, 4, 4, 4)
        self.detail_layout.setSpacing(12)

        top = QHBoxLayout()
        self.event_title = QLabel("Event")
        self.event_title.setObjectName("PageTitle")
        top.addWidget(self.event_title, 1)
        self.period = QComboBox()
        for label, value in self.PERIODS:
            self.period.addItem(label, value)
        self._select_period(self.config.period_days)
        self.period.currentIndexChanged.connect(self.load_local)
        top.addWidget(self.period)
        self.limit = QSpinBox()
        self.limit.setRange(10, 5000)
        self.limit.setValue(self.config.sync_limit)
        self.limit.setSuffix(" max")
        top.addWidget(self.limit)
        self.count_button = QPushButton("Server count")
        self.count_button.clicked.connect(self.server_count)
        top.addWidget(self.count_button)
        self.sync_button = QPushButton("Sync new")
        self.sync_button.setObjectName("PrimaryButton")
        self.sync_button.clicked.connect(self.sync)
        top.addWidget(self.sync_button)
        self.detail_layout.addLayout(top)

        self.description = QLabel("")
        self.description.setObjectName("PageSubtitle")
        self.description.setWordWrap(True)
        self.detail_layout.addWidget(self.description)

        self.status = QLabel("No Firebase request is performed automatically.")
        self.status.setObjectName("Muted")
        self.detail_layout.addWidget(self.status)

        filters_panel = QFrame()
        filters_panel.setObjectName("Panel")
        filters_layout = QVBoxLayout(filters_panel)
        filters_layout.setContentsMargins(14, 12, 14, 12)
        filters_title = QLabel("Filters")
        filters_title.setObjectName("SectionTitle")
        filters_layout.addWidget(filters_title)
        self.filters_form = QFormLayout()
        filters_layout.addLayout(self.filters_form)
        self.detail_layout.addWidget(filters_panel)

        metric_row = QHBoxLayout()
        self.cached_count = MetricCard("Cached events")
        self.server_count_card = MetricCard("Server count", hint="Only updated when requested")
        metric_row.addWidget(self.cached_count)
        metric_row.addWidget(self.server_count_card)
        self.detail_layout.addLayout(metric_row)

        self.activity = ActivityChart()
        self.detail_layout.addWidget(self.activity)

        self.insights = QGridLayout()
        self.detail_layout.addLayout(self.insights)

        recent_panel = QFrame()
        recent_panel.setObjectName("Panel")
        recent_layout = QVBoxLayout(recent_panel)
        recent_layout.addWidget(QLabel("Recent cached events"))
        self.recent = QListWidget()
        self.recent.setMinimumHeight(230)
        recent_layout.addWidget(self.recent)
        self.detail_layout.addWidget(recent_panel)
        self.detail_layout.addStretch()
        splitter.addWidget(self.detail)
        splitter.setSizes([270, 950])

        if self.config.events:
            self.events_list.setCurrentRow(0)

    def _select_event(self, row: int) -> None:
        if row < 0 or row >= len(self.config.events):
            return
        self.current_event = self.config.events[row]
        self.event_title.setText(self.current_event.title)
        self.description.setText(self.current_event.description or self.current_event.name)
        self._rebuild_filters()
        self._rebuild_insights()
        self.server_count_card.set_value("—")
        self.load_local()

    def _rebuild_filters(self) -> None:
        while self.filters_form.rowCount():
            self.filters_form.removeRow(0)
        self.filter_widgets.clear()
        if not self.current_event:
            return
        for property_definition in self.current_event.properties:
            if not property_definition.filterable:
                continue
            if property_definition.kind == "bool":
                widget = QComboBox()
                widget.addItem("Any", None)
                widget.addItem("True", True)
                widget.addItem("False", False)
                widget.currentIndexChanged.connect(self.load_local)
            else:
                widget = QLineEdit()
                widget.setPlaceholderText("Any")
                widget.editingFinished.connect(self.load_local)
            self.filter_widgets[property_definition.key] = (property_definition, widget)
            self.filters_form.addRow(property_definition.title, widget)

    def _current_filters(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for key, (definition, widget) in self.filter_widgets.items():
            if definition.kind == "bool":
                value = widget.currentData()
                if value is not None:
                    values[key] = bool(value)
                continue
            raw = widget.text().strip()
            if not raw:
                continue
            if definition.kind == "int":
                try:
                    values[key] = int(raw)
                except ValueError:
                    continue
            elif definition.kind == "double":
                try:
                    values[key] = float(raw)
                except ValueError:
                    continue
            else:
                values[key] = raw
        return values

    def _rebuild_insights(self) -> None:
        while self.insights.count():
            item = self.insights.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.ranking_cards.clear()
        if not self.current_event:
            return
        for index, insight in enumerate(self.current_event.insights):
            card = RankingCard(insight.title)
            self.ranking_cards.append((insight, card))
            self.insights.addWidget(card, index // 2, index % 2)

    def load_local(self) -> None:
        if not self.current_event:
            return
        days = self.period.currentData()
        name = self.current_event.name
        filters = self._current_filters()
        self.cached_count.set_value(
            self.project.analytics.local_count(
                event_name=name,
                days=days,
                property_filters=filters,
            )
        )
        self.activity.set_data(
            self.project.analytics.local_activity_by_day(
                event_name=name,
                days=days,
                property_filters=filters,
            )
        )

        for insight, card in self.ranking_cards:
            values: dict[str, int] = {}
            if insight.kind in ("top_values", "bool_distribution") and insight.property_key:
                values = self.project.analytics.local_property_counts(
                    insight.property_key,
                    event_name=name,
                    days=days,
                    top=insight.limit,
                    property_filters=filters,
                )
            elif insight.kind == "average" and insight.property_key:
                average = self.project.analytics.local_average(
                    insight.property_key,
                    event_name=name,
                    days=days,
                    property_filters=filters,
                )
                values = {"Average": round(average, 2)} if average is not None else {}
            card.set_values(values)

        self.recent.clear()
        events = self.project.analytics.local_events(
            event_name=name,
            days=days,
            limit=self.config.recent_limit,
            property_filters=filters,
        )
        for event in events:
            properties = event.get("properties") if isinstance(event.get("properties"), dict) else {}
            summary = " · ".join(f"{key}: {value}" for key, value in list(properties.items())[:4])
            item = QListWidgetItem(f"{format_timestamp(event.get('timestamp'))}\n{summary or 'No properties'}")
            self.recent.addItem(item)

        last_sync = self.project.analytics.last_sync(
            event_name=name,
            days=days,
            property_filters=filters,
        )
        self.status.setText(
            f"Cached locally · last sync {last_sync.astimezone().strftime('%Y-%m-%d %H:%M')}"
            if last_sync
            else "Not synchronized for this event/period. No Firebase request has been made."
        )

    def sync(self) -> None:
        if not self.current_event:
            return
        self.sync_button.setEnabled(False)
        self.sync_button.setText("Syncing…")
        name = self.current_event.name
        days = self.period.currentData()
        limit = self.limit.value()
        filters = self._current_filters()
        self.run_task(
            lambda: self.project.analytics.sync_events(
                event_name=name,
                days=days,
                limit=limit,
                property_filters=filters,
            ),
            on_result=self._sync_result,
            on_error=self._show_error,
            on_finished=self._finish_sync,
        )

    def server_count(self) -> None:
        if not self.current_event:
            return
        self.count_button.setEnabled(False)
        name = self.current_event.name
        days = self.period.currentData()
        filters = self._current_filters()
        self.run_task(
            lambda: self.project.analytics.count_events(
                event_name=name,
                days=days,
                property_filters=filters,
            ),
            on_result=lambda value: self.server_count_card.set_value(value),
            on_error=self._show_error,
            on_finished=lambda: self.count_button.setEnabled(True),
        )

    def _sync_result(self, result: dict[str, Any]) -> None:
        self.load_local()
        suffix = " Sync again to continue." if result.get("has_more") else ""
        self.status.setText(f"Fetched {result.get('fetched', 0)} new events.{suffix}")

    def _finish_sync(self) -> None:
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Sync new")

    def _show_error(self, error: Exception) -> None:
        QMessageBox.critical(self, "FirebaseAppUtilities", str(error))

    def _select_period(self, days: int | None) -> None:
        for index in range(self.period.count()):
            if self.period.itemData(index) == days:
                self.period.setCurrentIndex(index)
                return
