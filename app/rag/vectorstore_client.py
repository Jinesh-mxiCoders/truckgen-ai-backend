import json
from sqlalchemy import text
from app.core.database import Database

class VectorStoreClient:
    """
    Class to handle CRUD operations for vector embeddings in PGVector.
    """

    def __init__(self, db: Database):
        self.db = db

    def upsert_embedding(
        self,
        product_type: str,
        model: str | None,
        text_chunk: str,
        metadata: dict,
        embedding: list[float]
    ):
        """
        Insert a new embedding into technical_docs table.
        """
        try:
            with self.db.engine.begin() as conn:
                conn.execute(
                    text("""
                    INSERT INTO technical_docs (product_type, model, chunk, metadata, embedding)
                    VALUES (:product_type, :model, :chunk, :metadata, :embedding)
                    ON CONFLICT (product_type, model, chunk)
                    DO UPDATE SET metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding;
                    """),
                    {
                        "product_type": product_type,
                        "model": model,
                        "chunk": text_chunk,
                        "metadata": json.dumps(metadata),
                        "embedding": embedding
                    }
                )
        except Exception as e:
            print(f"❌ Failed to upsert embedding: {e}")

vector_client = VectorStoreClient(Database())