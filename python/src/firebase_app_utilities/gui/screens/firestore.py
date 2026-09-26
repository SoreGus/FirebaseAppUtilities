from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...core.project import FirebaseProject
from ..tasks import TaskHost
from ..widgets import Inspector, json_text


class FirestoreScreen(QWidget, TaskHost):
    def __init__(
        self,
        project: FirebaseProject,
        parent: QWidget | None = None,
    ):
        QWidget.__init__(self, parent)
        TaskHost.__init__(self)
        self.project = project
        self._documents: list[dict[str, Any]] = []
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Firestore")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Browse collections and inspect documents without leaving the utility.")
        subtitle.setObjectName("PageSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        refresh = QPushButton("Reload collections")
        refresh.setObjectName("PrimaryButton")
        refresh.clicked.connect(self.refresh)
        header.addWidget(refresh)
        layout.addLayout(header)

        splitter = QSplitter()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        collections_title = QLabel("Collections")
        collections_title.setObjectName("SectionTitle")
        left_layout.addWidget(collections_title)
        self.collections = QListWidget()
        self.collections.currentTextChanged.connect(self._load_collection)
        left_layout.addWidget(self.collections)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.documents_title = QLabel("Documents")
        self.documents_title.setObjectName("SectionTitle")
        center_layout.addWidget(self.documents_title)
        self.documents = QTableWidget(0, 2)
        self.documents.setHorizontalHeaderLabels(["Document ID", "Preview"])
        self.documents.horizontalHeader().setStretchLastSection(True)
        self.documents.verticalHeader().setVisible(False)
        self.documents.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.documents.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.documents.itemSelectionChanged.connect(self._document_selected)
        center_layout.addWidget(self.documents)

        self.inspector = Inspector("Document")
        self.inspector.setMinimumWidth(330)

        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(self.inspector)
        splitter.setSizes([220, 650, 350])
        layout.addWidget(splitter, 1)

    def refresh(self) -> None:
        self.run_task(
            self.project.firestore.list_collections,
            on_result=self._apply_collections,
            on_error=self._show_error,
        )

    def _apply_collections(self, collections: list[str]) -> None:
        self.collections.clear()
        self.collections.addItems(collections)
        if collections:
            self.collections.setCurrentRow(0)

    def _load_collection(self, collection: str) -> None:
        if not collection:
            return
        self.documents_title.setText(collection)
        self.run_task(
            lambda: self.project.firestore.list_documents(collection, limit=250),
            on_result=self._apply_documents,
            on_error=self._show_error,
        )

    def _apply_documents(self, documents: list[dict[str, Any]]) -> None:
        self._documents = documents
        self.documents.setRowCount(len(documents))

        for row, document in enumerate(documents):
            document_id = str(document.get("id", ""))
            preview = {key: value for key, value in document.items() if key != "id"}
            id_item = QTableWidgetItem(document_id)
            id_item.setData(Qt.ItemDataRole.UserRole, row)
            self.documents.setItem(row, 0, id_item)
            self.documents.setItem(row, 1, QTableWidgetItem(json_text(preview).replace("\n", " ")[:240]))

        self.documents.resizeColumnsToContents()
        self.documents.setColumnWidth(0, 220)

    def _document_selected(self) -> None:
        row = self.documents.currentRow()
        if 0 <= row < len(self._documents):
            self.inspector.show_document(self._documents[row])

    def _show_error(self, error: Exception) -> None:
        QMessageBox.critical(self, "FirebaseAppUtilities", str(error))
