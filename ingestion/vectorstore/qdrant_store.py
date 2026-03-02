from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import uuid


class QdrantVectorStore:
    def __init__(self, collection_name="refinery_docs", vector_size=384):
        
        self.client = QdrantClient(host="qdrant", port=6333)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if self.collection_name not in names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    def add_vectors(self, embeddings, metadatas):
        points = []

        for vector, meta in zip(embeddings, metadatas):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": meta
            })

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, vector, limit=10):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector.tolist(),
            limit=limit,
            with_payload=True
        )

        return results.points
