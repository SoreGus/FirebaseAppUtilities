from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..tasks import TaskHost


class FunctionsScreen(QWidget, TaskHost):
    def __init__(
        self,
        project: FirebaseProject,
        parent: QWidget | None = None,
    ):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Functions")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Call configured HTTP Firebase Functions and inspect the response.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)

        if not self.project.config.functions.base_url:
            card = QFrame()
            card.setObjectName("Card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            heading = QLabel("Functions are not configured")
            heading.setObjectName("SectionTitle")
            body = QLabel(
                "Add [functions].base_url to the project TOML when this project starts using HTTP Functions."
            )
            body.setObjectName("Muted")
            body.setWordWrap(True)
            card_layout.addWidget(heading)
            card_layout.addWidget(body)
            layout.addWidget(card)
            layout.addStretch()
            return

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(12)

        form = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("myFunction")
        self.method = QComboBox()
        self.method.addItems(["POST", "GET", "PUT", "PATCH", "DELETE"])
        form.addRow("Function", self.name)
        form.addRow("Method", self.method)
        form_layout.addLayout(form)

        self.payload = QPlainTextEdit()
        self.payload.setPlaceholderText('{\n  "hello": "world"\n}')
        self.payload.setMinimumHeight(150)
        form_layout.addWidget(self.payload)

        actions = QHBoxLayout()
        actions.addStretch()
        invoke = QPushButton("Invoke function")
        invoke.setObjectName("PrimaryButton")
        invoke.clicked.connect(self.invoke)
        actions.addWidget(invoke)
        form_layout.addLayout(actions)
        layout.addWidget(form_card)

        response_card = QFrame()
        response_card.setObjectName("Card")
        response_layout = QVBoxLayout(response_card)
        response_layout.setContentsMargins(18, 18, 18, 18)
        response_layout.addWidget(QLabel("Response"))
        self.response = QPlainTextEdit()
        self.response.setReadOnly(True)
        response_layout.addWidget(self.response)
        layout.addWidget(response_card, 1)

    def invoke(self) -> None:
        name = self.name.text().strip()
        if not name:
            QMessageBox.information(self, "FirebaseAppUtilities", "Enter a function name.")
            return

        raw = self.payload.toPlainText().strip()
        try:
            payload = json.loads(raw) if raw else None
        except ValueError as error:
            QMessageBox.warning(self, "Invalid JSON", str(error))
            return

        method = self.method.currentText()

        def call():
            response = self.project.functions.request(name, method=method, json=payload)
            try:
                return json.dumps(response.json(), indent=2, ensure_ascii=False)
            except ValueError:
                return response.text

        self.response.setPlainText("Loading…")
        self.run_task(
            call,
            on_result=self.response.setPlainText,
            on_error=lambda error: QMessageBox.critical(
                self,
                "FirebaseAppUtilities",
                str(error),
            ),
        )
