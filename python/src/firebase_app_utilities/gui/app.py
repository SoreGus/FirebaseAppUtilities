from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.project import FirebaseProject
from .models import AnalyticsDashboardConfig
from .screens import (
    DashboardScreen,
    EventsScreen,
    FirestoreScreen,
    FunctionsScreen,
    ProjectScreen,
)
from .theme import apply_theme

GuiExtension = Callable[["FirebaseUtilitiesWindow"], None]


class NavigationRail(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(210)
        self.buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(6)

        brand = QHBoxLayout()
        mark = QLabel("F")
        mark.setObjectName("BrandMark")
        mark.setFixedSize(38, 38)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.addWidget(mark)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        name = QLabel(title)
        name.setStyleSheet("font-weight: 700; font-size: 14px;")
        product = QLabel("Firebase utilities")
        product.setObjectName("Muted")
        brand_text.addWidget(name)
        brand_text.addWidget(product)
        brand.addLayout(brand_text, 1)
        layout.addLayout(brand)
        layout.addSpacing(22)

        self.nav_layout = layout
        layout.addStretch()

    def add_item(
        self,
        key: str,
        title: str,
        on_click: Callable[[], None],
        *,
        bottom: bool = False,
    ) -> QPushButton:
        button = QPushButton(title)
        button.setObjectName("NavButton")
        button.setCheckable(True)
        button.clicked.connect(on_click)

        if bottom:
            self.nav_layout.addWidget(button)
        else:
            stretch_index = self.nav_layout.count() - 1
            self.nav_layout.insertWidget(stretch_index, button)

        self.buttons[key] = button
        return button

    def select(self, key: str) -> None:
        for item_key, button in self.buttons.items():
            button.setChecked(item_key == key)


class FirebaseUtilitiesWindow(QMainWindow):
    def __init__(
        self,
        *,
        project: FirebaseProject,
        title: str = "FirebaseAppUtilities",
        analytics: AnalyticsDashboardConfig | None = None,
        extensions: Iterable[GuiExtension] = (),
    ):
        super().__init__()
        self.project = project
        self.analytics_config = analytics or AnalyticsDashboardConfig()
        self.extensions = tuple(extensions)
        self.setWindowTitle(title)
        self.resize(1360, 860)
        self.setMinimumSize(1060, 680)

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.navigation = NavigationRail(title)
        root_layout.addWidget(self.navigation)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        self._screens: dict[str, QWidget] = {}
        self._build_screens()

        for extension in self.extensions:
            extension(self)

        self.show_screen("dashboard")

    def _build_screens(self) -> None:
        self.register_screen(
            "dashboard",
            "Dashboard",
            DashboardScreen(self.project, self.analytics_config),
        )
        self.register_screen(
            "events",
            "Events",
            EventsScreen(self.project, self.analytics_config),
        )
        self.register_screen(
            "firestore",
            "Firestore",
            FirestoreScreen(self.project),
        )
        self.register_screen(
            "functions",
            "Functions",
            FunctionsScreen(self.project),
        )
        self.register_screen(
            "project",
            "Project",
            ProjectScreen(self.project),
            bottom=True,
        )

    def register_screen(
        self,
        key: str,
        title: str,
        widget: QWidget,
        *,
        bottom: bool = False,
    ) -> None:
        self._screens[key] = widget
        self.stack.addWidget(widget)
        self.navigation.add_item(
            key,
            title,
            lambda checked=False, screen_key=key: self.show_screen(screen_key),
            bottom=bottom,
        )

    def show_screen(self, key: str) -> None:
        widget = self._screens[key]
        self.stack.setCurrentWidget(widget)
        self.navigation.select(key)

        refresh = getattr(widget, "refresh", None)
        if callable(refresh):
            refresh()


class ConnectionWindow(QMainWindow):
    def __init__(
        self,
        *,
        title: str,
        analytics: AnalyticsDashboardConfig | None,
        extensions: Iterable[GuiExtension],
    ):
        super().__init__()
        self.title_text = title
        self.analytics = analytics
        self.extensions = tuple(extensions)
        self.child: FirebaseUtilitiesWindow | None = None
        self.setWindowTitle(title)
        self.setFixedSize(620, 420)

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(50, 48, 50, 48)
        layout.setSpacing(16)

        mark = QLabel("F")
        mark.setObjectName("BrandMark")
        mark.setFixedSize(48, 48)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mark)

        heading = QLabel("Connect a Firebase project")
        heading.setObjectName("PageTitle")
        layout.addWidget(heading)

        body = QLabel(
            "Choose the local TOML configuration for the project you want to inspect. "
            "The path is only used to establish the connection and is not shown in the workspace."
        )
        body.setObjectName("PageSubtitle")
        body.setWordWrap(True)
        layout.addWidget(body)
        layout.addStretch()

        button = QPushButton("Choose project configuration")
        button.setObjectName("PrimaryButton")
        button.clicked.connect(self.choose)
        layout.addWidget(button)

    def choose(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Firebase project configuration",
            "",
            "TOML (*.toml);;All files (*)",
        )
        if not path:
            return

        try:
            project = FirebaseProject.from_toml(path)
        except Exception as error:
            QMessageBox.critical(self, "FirebaseAppUtilities", str(error))
            return

        self.child = FirebaseUtilitiesWindow(
            project=project,
            title=self.title_text,
            analytics=self.analytics,
            extensions=self.extensions,
        )
        self.child.show()
        self.close()


class FirebaseUtilitiesApp:
    def __init__(
        self,
        *,
        project: FirebaseProject | None = None,
        config_path: str | Path | None = None,
        title: str = "FirebaseAppUtilities",
        analytics: AnalyticsDashboardConfig | None = None,
        extensions: Iterable[GuiExtension] = (),
    ):
        self.project = project
        self.config_path = Path(config_path).expanduser() if config_path else None
        self.title = title
        self.analytics = analytics
        self.extensions = tuple(extensions)

    @classmethod
    def from_toml(
        cls,
        path: str | Path,
        *,
        title: str = "FirebaseAppUtilities",
        analytics: AnalyticsDashboardConfig | None = None,
        extensions: Iterable[GuiExtension] = (),
    ) -> "FirebaseUtilitiesApp":
        return cls(
            project=FirebaseProject.from_toml(path),
            config_path=path,
            title=title,
            analytics=analytics,
            extensions=extensions,
        )

    def run(self) -> int:
        app = QApplication.instance()
        owns_app = app is None

        if app is None:
            app = QApplication(sys.argv)

        apply_theme(app)

        project = self.project
        if project is None and self.config_path and self.config_path.exists():
            project = FirebaseProject.from_toml(self.config_path)

        if project is not None:
            window: QMainWindow = FirebaseUtilitiesWindow(
                project=project,
                title=self.title,
                analytics=self.analytics,
                extensions=self.extensions,
            )
        else:
            window = ConnectionWindow(
                title=self.title,
                analytics=self.analytics,
                extensions=self.extensions,
            )

        window.show()

        if owns_app:
            return app.exec()
        return 0


def run_gui(
    initial_config: str | Path | None = None,
    *,
    project: FirebaseProject | None = None,
    title: str = "FirebaseAppUtilities",
    analytics: AnalyticsDashboardConfig | None = None,
    extensions: Iterable[GuiExtension] = (),
) -> int:
    return FirebaseUtilitiesApp(
        project=project,
        config_path=initial_config,
        title=title,
        analytics=analytics,
        extensions=extensions,
    ).run()
