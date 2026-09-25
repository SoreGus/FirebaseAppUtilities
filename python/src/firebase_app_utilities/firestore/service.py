from __future__ import annotations

from typing import Any

from google.cloud.firestore_v1 import Client


class FirestoreService:
    def __init__(self, client: Client):
        self._client = client

    def list_collections(self) -> list[str]:
        return sorted(collection.id for collection in self._client.collections())

    def list_documents(self, collection: str, limit: int = 50) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for snapshot in self._client.collection(collection).limit(limit).stream():
            result.append({"id": snapshot.id, **(snapshot.to_dict() or {})})
        return result

    def get_document(self, collection: str, document_id: str) -> dict[str, Any] | None:
        snapshot = self._client.collection(collection).document(document_id).get()
        if not snapshot.exists:
            return None
        return {"id": snapshot.id, **(snapshot.to_dict() or {})}

    def set_document(
        self,
        collection: str,
        document_id: str,
        data: dict[str, Any],
        *,
        merge: bool = True,
    ) -> None:
        self._client.collection(collection).document(document_id).set(data, merge=merge)

    def delete_document(self, collection: str, document_id: str) -> None:
        self._client.collection(collection).document(document_id).delete()
