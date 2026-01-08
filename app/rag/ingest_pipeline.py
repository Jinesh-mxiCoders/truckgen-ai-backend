from app.rag.normalizer import ProductNormalizer
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vectorstore_client import VectorStoreClient

class BasePipeline:
    """
    Abstract pipeline class for ingesting products into vector store.
    Subclasses must implement `ingest` method.
    """

    def __init__(self, normalizer: ProductNormalizer, embedder: EmbeddingGenerator, vector_client: VectorStoreClient):
        self.normalizer = normalizer
        self.embedder = embedder
        self.vector_client = vector_client

    def ingest(self, source_path: str):
        raise NotImplementedError("Subclasses must implement `ingest` method.")


class JSONPipeline(BasePipeline):
    """
    Pipeline to ingest products from a JSON file.
    """

    @staticmethod
    def build_embedding_text(spec_row: dict) -> str:
        return f"{spec_row['product_type']} model {spec_row['model']} {spec_row['field_key']} is {spec_row['raw_text']}"

    def ingest(self, json_path: str):
        import json

        print(f"📥 Ingesting JSON file: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        print(f"Loaded {len(items)} products from JSON")

        for item in items:
            # 1️. Normalize product
            rows = self.normalizer.normalize_product(item)
            # 2️. Build embedding texts
            chunks = [self.build_embedding_text(r) for r in rows]
            print("Generating embedding for", len(chunks), "chunks...")
            # 3. Generate embeddings
            embeddings = self.embedder.embed_documents(chunks)
            # 4️. Upsert into vector store
            for row, chunk, embedding in zip(rows, chunks, embeddings):
                metadata = {
                    "field_key": row["field_key"],
                    "field_type": row["field_type"],
                    "unit": row["unit"],
                    "numeric_value": row["numeric_value"],
                    "text_value": row["text_value"],
                    "raw_text": row["raw_text"],
                    "source_url": item.get("source_url"),
                    "brochure_url": item.get("brochure_url")
                }
                self.vector_client.upsert_embedding(
                    product_type=row["product_type"],
                    model=row["model"],
                    text_chunk=chunk,
                    metadata=metadata,
                    embedding=embedding
                )
