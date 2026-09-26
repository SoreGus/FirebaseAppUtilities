from __future__ import annotations

from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

from ..analytics.service import AnalyticsService
from ..firestore.service import FirestoreService
from ..functions.service import FunctionsService
from .config import UtilitiesConfig


class FirebaseProject:
    """Connected Firebase project and entry point for reusable services."""

    def __init__(self, config: UtilitiesConfig):
        self.config = config
        self._app = self._initialize_app(config)
        self._firestore_client = firestore.client(app=self._app)

        self.firestore = FirestoreService(self._firestore_client)
        self.analytics = AnalyticsService(
            self._firestore_client,
            collection=config.analytics.collection,
        )
        self.functions = FunctionsService(
            config.functions.base_url
        )

    @classmethod
    def from_toml(
        cls,
        path: str | Path,
    ) -> "FirebaseProject":
        return cls(
            UtilitiesConfig.from_toml(path)
        )

    @staticmethod
    def _initialize_app(
        config: UtilitiesConfig,
    ) -> firebase_admin.App:
        app_name = (
            "firebase-app-utilities:"
            f"{config.project.project_id}:"
            f"{config.project.environment}"
        )

        try:
            return firebase_admin.get_app(app_name)
        except ValueError:
            pass

        options: dict[str, Any] = {
            "projectId": config.project.project_id
        }

        if config.project.credentials:
            credential = credentials.Certificate(
                str(config.project.credentials)
            )

            return firebase_admin.initialize_app(
                credential,
                options=options,
                name=app_name,
            )

        return firebase_admin.initialize_app(
            options=options,
            name=app_name,
        )

    @property
    def project_id(self) -> str:
        return self.config.project.project_id

    @property
    def environment(self) -> str:
        return self.config.project.environment

    def status(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "environment": self.environment,
            "credentials": (
                str(self.config.project.credentials)
                if self.config.project.credentials
                else "application-default"
            ),
            "analytics_collection": self.config.analytics.collection,
            "functions_base_url": self.config.functions.base_url,
        }
