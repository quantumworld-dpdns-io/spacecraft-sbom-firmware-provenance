from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sbom_provenance.config import get_settings


class VectorStore(ABC):
    @abstractmethod
    async def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def query(
        self,
        query_embeddings: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        ...

    @abstractmethod
    async def count(self) -> int:
        ...


class ChromaVectorStore(VectorStore):
    def __init__(self) -> None:
        import chromadb
        settings = get_settings()
        self.client = chromadb.HttpClient(
            host=settings.vector_db_url.replace("http://", "").split(":")[0],
            port=int(settings.vector_db_url.split(":")[-1]),
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.vector_db_collection,
        )

    async def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    async def query(
        self,
        query_embeddings: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=top_k,
            where=filter,
        )
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else 0,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "document": results["documents"][0][i] if results.get("documents") else "",
            })
        return output

    async def delete(self, ids: list[str]) -> None:
        self.collection.delete(ids=ids)

    async def count(self) -> int:
        return self.collection.count()


class QdrantVectorStore(VectorStore):
    def __init__(self) -> None:
        from qdrant_client import QdrantClient, models
        settings = get_settings()
        self.client = QdrantClient(
            host=settings.vector_db_url.replace("http://", "").split(":")[0],
            port=int(settings.vector_db_url.split(":")[-1]),
        )
        self.collection_name = settings.vector_db_collection
        self.models = models
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.models.VectorParams(
                    size=get_settings().embedding_dimension,
                    distance=self.models.Distance.COSINE,
                ),
            )

    async def add_embeddings(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        points = []
        for i, _id in enumerate(ids):
            payload: dict[str, Any] = {}
            if metadatas and i < len(metadatas):
                payload.update(metadatas[i])
            if documents and i < len(documents):
                payload["document"] = documents[i]
            points.append(
                self.models.PointStruct(
                    id=hash(_id) % (2**63),
                    vector=embeddings[i],
                    payload=payload,
                )
            )
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def query(
        self,
        query_embeddings: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        qfilter = None
        if filter:
            qfilter = self.models.Filter(**self._dict_to_filter(filter))
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embeddings,
            limit=top_k,
            query_filter=qfilter,
        )
        return [
            {
                "id": str(p.id),
                "score": p.score,
                "metadata": p.payload or {},
                "document": (p.payload or {}).get("document", ""),
            }
            for p in results.points
        ]

    async def delete(self, ids: list[str]) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=self.models.PointIdsList(
                points=[hash(_id) % (2**63) for _id in ids]
            ),
        )

    async def count(self) -> int:
        return self.client.count(collection_name=self.collection_name).count

    def _dict_to_filter(self, d: dict, parent_key: str = "") -> dict:
        return d  # Simplified; real mapping would handle Qdrant filter syntax


def get_vector_store() -> VectorStore:
    settings = get_settings()
    if settings.vector_db_provider == "chroma":
        return ChromaVectorStore()
    elif settings.vector_db_provider == "qdrant":
        return QdrantVectorStore()
    else:
        return ChromaVectorStore()
