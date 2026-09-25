from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from ..core.project import FirebaseProject

GuiExtension = Callable[["FirebaseUtilitiesWindow", ttk.Notebook], None]


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


class FirebaseUtilitiesWindow(tk.Tk):
    """Reusable FirebaseAppUtilities Tk window.

    A connected FirebaseProject may be injected by a consuming project.
    When no project is provided, the generic window can connect from a TOML
    configuration file.
    """

    def __init__(
        self,
        *,
        project: FirebaseProject | None = None,
        initial_config: str | None = None,
        title: str = "FirebaseAppUtilities",
        extensions: Iterable[GuiExtension] = (),
    ):
        super().__init__()
        self.title(title)
        self.geometry("980x680")
        self.minsize(760, 520)

        self.project = project
        self.config_var = tk.StringVar(value=initial_config or "")
        self.status_var = tk.StringVar(value="Not connected")
        self.collection_var = tk.StringVar()
        self.event_var = tk.StringVar()
        self.limit_var = tk.IntVar(value=100)
        self._extensions = list(extensions)

        self._build_ui()

        if self.project is not None:
            self._refresh_project_state()
        elif initial_config and Path(initial_config).expanduser().exists():
            self.after(100, self.connect)

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Config").pack(side="left")
        ttk.Entry(top, textvariable=self.config_var).pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
        )
        ttk.Button(top, text="Browse", command=self.browse).pack(side="left")
        ttk.Button(top, text="Connect", command=self.connect).pack(
            side="left",
            padx=(8, 0),
        )

        status = ttk.Frame(self, padding=(12, 0, 12, 8))
        status.pack(fill="x")
        ttk.Label(status, textvariable=self.status_var).pack(side="left")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.project_tab = ttk.Frame(self.notebook, padding=12)
        self.firestore_tab = ttk.Frame(self.notebook, padding=12)
        self.analytics_tab = ttk.Frame(self.notebook, padding=12)
        self.functions_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.project_tab, text="Project")
        self.notebook.add(self.firestore_tab, text="Firestore")
        self.notebook.add(self.analytics_tab, text="Analytics")
        self.notebook.add(self.functions_tab, text="Functions")

        self.project_text = self._text_area(self.project_tab)

        fire_controls = ttk.Frame(self.firestore_tab)
        fire_controls.pack(fill="x", pady=(0, 8))
        ttk.Button(
            fire_controls,
            text="Collections",
            command=self.load_collections,
        ).pack(side="left")
        ttk.Entry(
            fire_controls,
            textvariable=self.collection_var,
            width=28,
        ).pack(side="left", padx=8)
        ttk.Button(
            fire_controls,
            text="Documents",
            command=self.load_documents,
        ).pack(side="left")

        self.firestore_text = self._text_area(self.firestore_tab)

        analytics_controls = ttk.Frame(self.analytics_tab)
        analytics_controls.pack(fill="x", pady=(0, 8))

        ttk.Label(analytics_controls, text="Event").pack(side="left")
        ttk.Entry(
            analytics_controls,
            textvariable=self.event_var,
            width=24,
        ).pack(side="left", padx=8)

        ttk.Label(analytics_controls, text="Limit").pack(side="left")
        ttk.Spinbox(
            analytics_controls,
            from_=1,
            to=5000,
            textvariable=self.limit_var,
            width=7,
        ).pack(side="left", padx=8)

        ttk.Button(
            analytics_controls,
            text="Events",
            command=self.load_analytics,
        ).pack(side="left")
        ttk.Button(
            analytics_controls,
            text="Counts",
            command=self.load_analytics_counts,
        ).pack(side="left", padx=8)

        self.analytics_text = self._text_area(self.analytics_tab)

        ttk.Label(
            self.functions_tab,
            text=(
                "HTTP function calls are available through the Python library and CLI.\n"
                "Use project.functions.request(...) or `firebase-app-utils function ...`."
            ),
            justify="left",
        ).pack(anchor="nw")

        for extension in self._extensions:
            extension(self, self.notebook)

    @staticmethod
    def _text_area(parent: ttk.Frame) -> tk.Text:
        text = tk.Text(parent, wrap="none", font=("Menlo", 12))
        text.pack(fill="both", expand=True)
        return text

    def browse(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select FirebaseAppUtilities TOML",
            filetypes=[("TOML", "*.toml"), ("All files", "*")],
        )
        if selected:
            self.config_var.set(selected)

    def connect(self) -> None:
        config_path = self.config_var.get().strip()
        if not config_path:
            messagebox.showinfo(
                "FirebaseAppUtilities",
                "Select a TOML configuration file first.",
            )
            return

        try:
            self.project = FirebaseProject.from_toml(config_path)
            self._refresh_project_state()
        except Exception as error:
            self.project = None
            self.status_var.set("Connection failed")
            messagebox.showerror("FirebaseAppUtilities", str(error))

    def _refresh_project_state(self) -> None:
        if self.project is None:
            self.status_var.set("Not connected")
            self._write(self.project_text, {})
            return

        self.status_var.set(
            f"Connected: {self.project.project_id} [{self.project.environment}]"
        )
        self._write(self.project_text, self.project.status())

    def _with_project(
        self,
        action: Callable[[FirebaseProject], Any],
        target: tk.Text,
    ) -> None:
        if self.project is None:
            messagebox.showinfo(
                "FirebaseAppUtilities",
                "Connect to a project first.",
            )
            return

        try:
            self._write(target, action(self.project))
        except Exception as error:
            messagebox.showerror("FirebaseAppUtilities", str(error))

    def load_collections(self) -> None:
        self._with_project(
            lambda project: project.firestore.list_collections(),
            self.firestore_text,
        )

    def load_documents(self) -> None:
        collection = self.collection_var.get().strip()
        if not collection:
            messagebox.showinfo(
                "FirebaseAppUtilities",
                "Enter a collection name.",
            )
            return

        self._with_project(
            lambda project: project.firestore.list_documents(
                collection,
                limit=self.limit_var.get(),
            ),
            self.firestore_text,
        )

    def load_analytics(self) -> None:
        event = self.event_var.get().strip() or None

        self._with_project(
            lambda project: project.analytics.list_events(
                event_name=event,
                limit=self.limit_var.get(),
            ),
            self.analytics_text,
        )

    def load_analytics_counts(self) -> None:
        self._with_project(
            lambda project: project.analytics.count_by_name(
                limit=max(self.limit_var.get(), 100)
            ),
            self.analytics_text,
        )

    @staticmethod
    def _write(target: tk.Text, value: Any) -> None:
        target.delete("1.0", "end")
        target.insert(
            "1.0",
            json.dumps(
                value,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            ),
        )


class FirebaseUtilitiesApp:
    """High-level reusable GUI entry point for consuming projects."""

    def __init__(
        self,
        *,
        project: FirebaseProject | None = None,
        config_path: str | Path | None = None,
        title: str = "FirebaseAppUtilities",
        extensions: Iterable[GuiExtension] = (),
    ):
        self.project = project
        self.config_path = str(config_path) if config_path is not None else None
        self.title = title
        self.extensions = list(extensions)

    @classmethod
    def from_toml(
        cls,
        path: str | Path,
        *,
        title: str = "FirebaseAppUtilities",
        extensions: Iterable[GuiExtension] = (),
    ) -> "FirebaseUtilitiesApp":
        project = FirebaseProject.from_toml(path)
        return cls(
            project=project,
            config_path=path,
            title=title,
            extensions=extensions,
        )

    def run(self) -> None:
        window = FirebaseUtilitiesWindow(
            project=self.project,
            initial_config=self.config_path,
            title=self.title,
            extensions=self.extensions,
        )
        window.mainloop()


def run_gui(
    initial_config: str | Path | None = None,
    *,
    project: FirebaseProject | None = None,
    title: str = "FirebaseAppUtilities",
    extensions: Iterable[GuiExtension] = (),
) -> None:
    FirebaseUtilitiesApp(
        project=project,
        config_path=initial_config,
        title=title,
        extensions=extensions,
    ).run()
