from __future__ import annotations

from datetime import date, datetime
import json
from typing import Any

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .theme import ACCENT, BORDER, SURFACE_ALT, TEXT, TEXT_MUTED


def format_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        local = value.astimezone()
        return local.strftime("%b %d, %Y · %H:%M:%S")

    if isinstance(value, date):
        return value.isoformat()

    if value is None:
        return "—"

    return str(value)


def json_text(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Card")


class MetricCard(Card):
    def __init__(
        self,
        title: str,
        *,
        hint: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel("—")
        self.value_label.setObjectName("MetricValue")
        layout.addWidget(self.value_label)

        self.hint_label = QLabel(hint or "")
        self.hint_label.setObjectName("Muted")
        self.hint_label.setVisible(bool(hint))
        layout.addWidget(self.hint_label)
        layout.addStretch()

    def set_value(self, value: Any) -> None:
        self.value_label.setText(str(value))


class ActivityChart(Card):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._points: list[tuple[str, int]] = []
        self.setMinimumHeight(245)

    def set_data(self, values: list[dict[str, Any]]) -> None:
        self._points = [
            (str(item.get("date", "")), int(item.get("count", 0)))
            for item in values
        ]
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(20, 18, -20, -22)
        painter.setPen(QColor(TEXT))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(title_font)
        painter.drawText(rect.left(), rect.top() + 12, "Activity")

        chart = rect.adjusted(0, 34, 0, -8)
        painter.setPen(QPen(QColor(BORDER), 1))
        for index in range(4):
            y = chart.top() + (chart.height() * index / 3)
            painter.drawLine(chart.left(), int(y), chart.right(), int(y))

        if not self._points or max(value for _, value in self._points) == 0:
            painter.setPen(QColor(TEXT_MUTED))
            painter.drawText(
                chart,
                Qt.AlignmentFlag.AlignCenter,
                "No activity in this period",
            )
            return

        maximum = max(value for _, value in self._points)
        count = max(len(self._points), 2)
        path = QPainterPath()
        fill = QPainterPath()

        for index, (_, value) in enumerate(self._points):
            x = chart.left() + (chart.width() * index / (count - 1))
            normalized = value / maximum if maximum else 0
            y = chart.bottom() - (chart.height() * normalized * 0.9)
            point = QPointF(x, y)

            if index == 0:
                path.moveTo(point)
                fill.moveTo(chart.left(), chart.bottom())
                fill.lineTo(point)
            else:
                path.lineTo(point)
                fill.lineTo(point)

        fill.lineTo(chart.right(), chart.bottom())
        fill.closeSubpath()
        painter.fillPath(fill, QColor(124, 92, 252, 35))
        painter.setPen(QPen(QColor(ACCENT), 2.4))
        painter.drawPath(path)

        if self._points:
            painter.setPen(QColor(TEXT_MUTED))
            small = QFont()
            small.setPointSize(9)
            painter.setFont(small)
            painter.drawText(
                chart.left(),
                chart.bottom() + 18,
                self._points[0][0],
            )
            last = self._points[-1][0]
            metrics = painter.fontMetrics()
            painter.drawText(
                chart.right() - metrics.horizontalAdvance(last),
                chart.bottom() + 18,
                last,
            )


class RankingCard(Card):
    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.list)

    def set_values(self, values: dict[str, int]) -> None:
        self.list.clear()

        if not values:
            item = QListWidgetItem("No data yet")
            item.setForeground(QColor(TEXT_MUTED))
            self.list.addItem(item)
            return

        maximum = max(values.values())

        for value, count in values.items():
            item = QListWidgetItem()
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(2, 4, 2, 4)

            name = QLabel(value)
            count_label = QLabel(str(count))
            count_label.setObjectName("Muted")
            count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(name, 1)
            row_layout.addWidget(count_label)

            item.setSizeHint(row.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, row)


class EventTable(QTableWidget):
    event_selected = Signal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels([
            "Event",
            "Time",
            "Session",
            "Properties",
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(False)
        self._events: list[dict[str, Any]] = []
        self.itemSelectionChanged.connect(self._emit_selection)

    def set_events(
        self,
        events: list[dict[str, Any]],
        labels: dict[str, str] | None = None,
    ) -> None:
        labels = labels or {}
        self._events = events
        self.setRowCount(len(events))

        for row, event in enumerate(events):
            name = str(event.get("name", "—"))
            display_name = labels.get(name, name.replace("_", " ").title())
            properties = event.get("properties") or {}
            property_summary = ", ".join(
                f"{key}: {value}"
                for key, value in list(properties.items())[:3]
            )

            values = [
                display_name,
                format_timestamp(event.get("timestamp")),
                str(event.get("sessionId") or "—"),
                property_summary or "—",
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row)
                self.setItem(row, column, item)

        self.resizeColumnsToContents()
        if self.columnWidth(0) < 180:
            self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 190)
        self.setColumnWidth(2, 160)

    def _emit_selection(self) -> None:
        row = self.currentRow()

        if 0 <= row < len(self._events):
            self.event_selected.emit(self._events[row])


class Inspector(Card):
    def __init__(
        self,
        title: str = "Details",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.title = QLabel(title)
        self.title.setObjectName("SectionTitle")
        layout.addWidget(self.title)

        self.meta = QLabel("Select an item to inspect it.")
        self.meta.setObjectName("Muted")
        self.meta.setWordWrap(True)
        layout.addWidget(self.meta)

        self.content = QLabel("")
        self.content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.content.setWordWrap(True)
        self.content.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.content, 1)

    def show_event(
        self,
        event: dict[str, Any],
        labels: dict[str, str] | None = None,
    ) -> None:
        labels = labels or {}
        name = str(event.get("name", "Event"))
        self.title.setText(labels.get(name, name.replace("_", " ").title()))
        self.meta.setText(format_timestamp(event.get("timestamp")))

        fields = {
            "sessionId": event.get("sessionId"),
            "userId": event.get("userId"),
            "properties": event.get("properties") or {},
            "documentId": event.get("id"),
        }
        self.content.setText(json_text(fields))

    def show_document(self, document: dict[str, Any]) -> None:
        document_id = str(document.get("id", "Document"))
        self.title.setText(document_id)
        self.meta.setText("Firestore document")
        payload = {key: value for key, value in document.items() if key != "id"}
        self.content.setText(json_text(payload))
