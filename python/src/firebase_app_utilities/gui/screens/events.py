from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..models import AnalyticsDashboardConfig
from ..tasks import TaskHost
from ..widgets import EventTable, Inspector


class EventsScreen(QWidget, TaskHost):
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
        self._all_events: list[dict[str, Any]] = []
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Events")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Search, filter and inspect product events.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.event_filter = QComboBox()
        self.event_filter.addItem("All events", None)
        self.event_filter.currentIndexChanged.connect(self._filter)
        toolbar.addWidget(self.event_filter)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search events, sessions or properties…")
        self.search.textChanged.connect(self._filter)
        toolbar.addWidget(self.search, 1)

        refresh = QPushButton("Refresh")
        refresh.setObjectName("PrimaryButton")
        refresh.clicked.connect(self.refresh)
        toolbar.addWidget(refresh)
        layout.addLayout(toolbar)

        splitter = QSplitter()
        self.table = EventTable()
        self.inspector = Inspector("Event details")
        self.inspector.setMinimumWidth(310)
        self.table.event_selected.connect(
            lambda event: self.inspector.show_event(event, self.config.event_labels)
        )
        splitter.addWidget(self.table)
        splitter.addWidget(self.inspector)
        splitter.setSizes([850, 330])
        layout.addWidget(splitter, 1)

    def refresh(self) -> None:
        self.run_task(
            lambda: self.project.analytics.list_events(
                limit=max(self.config.recent_events_limit, 250)
            ),
            on_result=self._apply_events,
            on_error=lambda error: QMessageBox.critical(
                self,
                "FirebaseAppUtilities",
                str(error),
            ),
        )

    def _apply_events(self, events: list[dict[str, Any]]) -> None:
        self._all_events = events
        current = self.event_filter.currentData()
        names = sorted({str(item.get("name", "")) for item in events if item.get("name")})
        self.event_filter.blockSignals(True)
        self.event_filter.clear()
        self.event_filter.addItem("All events", None)
        for name in names:
            self.event_filter.addItem(
                self.config.event_labels.get(name, name.replace("_", " ").title()),
                name,
            )
        if current:
            index = self.event_filter.findData(current)
            if index >= 0:
                self.event_filter.setCurrentIndex(index)
        self.event_filter.blockSignals(False)
        self._filter()

    def _filter(self) -> None:
        event_name = self.event_filter.currentData()
        query = self.search.text().strip().lower()
        filtered = []

        for event in self._all_events:
            if event_name and event.get("name") != event_name:
                continue
            if query and query not in str(event).lower():
                continue
            filtered.append(event)

        self.table.set_events(filtered, self.config.event_labels)
