from typing import Dict
from app.rag.ingest_pipeline import BasePipeline, JSONPipeline
from app.rag.normalizer import ProductNormalizer
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vectorstore_client import VectorStoreClient
from app.core.database import Database


class KnowledgeLoader:
    """
    High-level entry point for ingesting knowledge into the vector store.
    Owns and wires all shared dependencies.
    """

    def __init__(self):
        self.db = Database()
        self.vector_client = VectorStoreClient(self.db)
        self.embedder = EmbeddingGenerator()
        self.normalizer = ProductNormalizer()

        # Pipeline registry
        self.pipelines: Dict[str, BasePipeline] = {
            "json": JSONPipeline(
                normalizer=self.normalizer,
                embedder=self.embedder,
                vector_client=self.vector_client,
            ),
            # "pdf": PDFPipeline(...),
        }

    def ingest(self, file_path: str, source_type: str = "json"):
        """
        Ingest knowledge from a given source.
        """
        pipeline = self.pipelines.get(source_type.lower())
        if not pipeline:
            raise ValueError(f"No pipeline registered for source type: {source_type}")

        pipeline.ingest(file_path)
