from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..models import SupportConfig
from ..tasks import TaskHost
from ..widgets import format_timestamp


class SupportScreen(QWidget, TaskHost):
    PERIODS = (("Today", 1), ("7 days", 7), ("30 days", 30), ("90 days", 90), ("All cached", None))

    def __init__(self, project: FirebaseProject, config: SupportConfig, parent: QWidget | None = None):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self.config = config
        self._build()
        self.load_local()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(14)

        title = QLabel(self.config.title)
        title.setObjectName("PageTitle")
        subtitle = QLabel(self.config.subtitle)
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QHBoxLayout()
        self.category = QComboBox()
        self.category.addItem("All categories", None)
        for value, label in self.config.categories.items():
            self.category.addItem(label, value)
        self.category.currentIndexChanged.connect(self.load_local)
        controls.addWidget(self.category)

        self.period = QComboBox()
        for label, value in self.PERIODS:
            self.period.addItem(label, value)
        self._select_period(self.config.period_days)
        self.period.currentIndexChanged.connect(self.load_local)
        controls.addWidget(self.period)

        self.limit = QSpinBox()
        self.limit.setRange(10, 5000)
        self.limit.setValue(self.config.sync_limit)
        self.limit.setSuffix(" max")
        controls.addWidget(self.limit)
        controls.addStretch()

        self.sync_button = QPushButton("Sync new messages")
        self.sync_button.setObjectName("PrimaryButton")
        self.sync_button.clicked.connect(self.sync)
        controls.addWidget(self.sync_button)
        layout.addLayout(controls)

        self.status = QLabel("Showing local cache only · no Firebase request has been made")
        self.status.setObjectName("Muted")
        layout.addWidget(self.status)

        self.messages = QListWidget()
        self.messages.setSpacing(6)
        layout.addWidget(self.messages, 1)

    def load_local(self) -> None:
        days = self.period.currentData()
        category = self.category.currentData()
        messages = self.project.append_only.local_documents(
            self.config.collection,
            days=days,
            category=category,
            limit=self.config.visible_limit,
        )
        self.messages.clear()
        for message in messages:
            category_value = str(message.get("category") or "other")
            category_label = self.config.categories.get(category_value, category_value.title())
            identity = str(message.get("name") or message.get("email") or "Anonymous")
            locale = str(message.get("locale") or "—")
            body = str(message.get("message") or "")
            text = (
                f"{category_label} · {identity} · {locale}\n"
                f"{body}\n"
                f"{format_timestamp(message.get(self.config.timestamp_field))}"
            )
            item = QListWidgetItem(text)
            item.setToolTip(str(message.get("email") or ""))
            self.messages.addItem(item)
        self.status.setText(f"{len(messages)} cached message(s) shown · Firebase is queried only when Sync is pressed")

    def sync(self) -> None:
        self.sync_button.setEnabled(False)
        self.sync_button.setText("Syncing…")
        days = self.period.currentData()
        limit = self.limit.value()
        self.run_task(
            lambda: self.project.append_only.sync(
                self.config.collection,
                timestamp_field=self.config.timestamp_field,
                days=days,
                limit=limit,
                sync_key=f"support:{self.config.collection}:{days}",
            ),
            on_result=self._sync_result,
            on_error=self._show_error,
            on_finished=self._finish,
        )

    def _sync_result(self, result: dict[str, Any]) -> None:
        self.load_local()
        suffix = " Sync again to continue." if result.get("has_more") else ""
        self.status.setText(f"Fetched {result.get('fetched', 0)} new message(s).{suffix}")

    def _finish(self) -> None:
        self.sync_button.setEnabled(True)
        self.sync_button.setText("Sync new messages")

    def _show_error(self, error: Exception) -> None:
        QMessageBox.critical(self, "FirebaseAppUtilities", str(error))

    def _select_period(self, days: int | None) -> None:
        for index in range(self.period.count()):
            if self.period.itemData(index) == days:
                self.period.setCurrentIndex(index)
                return
