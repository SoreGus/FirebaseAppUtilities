from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject


class ProjectScreen(QWidget):
    def __init__(
        self,
        project: FirebaseProject,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.project = project
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Project")
        title.setObjectName("PageTitle")
        layout.addWidget(title)
        subtitle = QLabel("Connection, environment and service configuration.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)

        identity = QFrame()
        identity.setObjectName("Card")
        identity_layout = QVBoxLayout(identity)
        identity_layout.setContentsMargins(20, 20, 20, 20)

        project_name = QLabel(self.project.project_id)
        project_name.setObjectName("PageTitle")
        identity_layout.addWidget(project_name)
        connected = QLabel(f"Connected · {self.project.environment}")
        connected.setObjectName("Success")
        identity_layout.addWidget(connected)
        layout.addWidget(identity)

        configuration = QFrame()
        configuration.setObjectName("Card")
        config_layout = QFormLayout(configuration)
        config_layout.setContentsMargins(20, 20, 20, 20)
        config_layout.setHorizontalSpacing(32)
        config_layout.setVerticalSpacing(14)

        credentials = (
            "Service account"
            if self.project.config.project.credentials
            else "Application Default Credentials"
        )
        values = [
            ("Project ID", self.project.project_id),
            ("Environment", self.project.environment),
            ("Credentials", credentials),
            ("Analytics collection", self.project.config.analytics.collection),
            ("Functions base URL", self.project.config.functions.base_url or "Not configured"),
        ]

        for label, value in values:
            key = QLabel(label)
            key.setObjectName("Muted")
            config_layout.addRow(key, QLabel(str(value)))

        layout.addWidget(configuration)
        layout.addStretch()
