from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud.firestore_v1 import Client


class AnalyticsService:
    def __init__(self, client: Client, collection: str = "analytics_events"):
        self._client = client
        self.collection = collection

    def list_events(
        self,
        *,
        event_name: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = self._client.collection(self.collection)
        if event_name:
            query = query.where("name", "==", event_name)
        query = query.order_by("timestamp", direction="DESCENDING").limit(limit)

        return [
            {"id": snapshot.id, **(snapshot.to_dict() or {})}
            for snapshot in query.stream()
        ]

    def count_by_name(self, *, days: int | None = None, limit: int = 5000) -> dict[str, int]:
        query = self._client.collection(self.collection)
        if days is not None:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where("timestamp", ">=", since)
        query = query.limit(limit)

        counter: Counter[str] = Counter()
        for snapshot in query.stream():
            name = (snapshot.to_dict() or {}).get("name")
            if isinstance(name, str) and name:
                counter[name] += 1
        return dict(counter.most_common())

    def unique_users(self, *, days: int | None = None, limit: int = 5000) -> int:
        query = self._client.collection(self.collection)
        if days is not None:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where("timestamp", ">=", since)
        query = query.limit(limit)

        users: set[str] = set()
        for snapshot in query.stream():
            user_id = (snapshot.to_dict() or {}).get("userId")
            if isinstance(user_id, str) and user_id:
                users.add(user_id)
        return len(users)
