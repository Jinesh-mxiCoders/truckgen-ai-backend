import json
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Database
from app.rag.embeddings import EmbeddingGenerator
import re
from collections import defaultdict

MODEL_REGEX = re.compile(r"model\s+(SP\s*[0-9\-]+)", re.I)


class RAGRetriever:
    """
    handles semantics retrieval from pgvec.
    """

    def __init__(self, db: Database, embedder: EmbeddingGenerator):
        self.db = db
        self.embedder = embedder

    async def retrieve(
        self,
        query: str,
        product_type: str | None = None,
        field_key: str | None = None,
        mode: str = "qa",   # qa | validation | range
        top_k: int = 5
    ) -> dict:
        try:
            raw_docs = await self._semantic_search(
                query=query,
                product_type=product_type,
                field_key=field_key,
                top_k=top_k
            )

            facts = self._normalize_docs(raw_docs)
            facts = self._reduce_to_valid_facts(facts)
            grouped = self._group_by_product_and_model(facts)

            return {
                "raw_docs": raw_docs,           # debugging / traceability
                "facts": facts,                 # flat normalized facts
                "grouped": grouped,             # product → model → specs
            }

        except Exception as err:
            raise RuntimeError("Error during RAG retrieval", err) from err

    async def retrieve_constraint_fields(
        self,
        query: str,
        product_type: str | None = None,
        field_key: str | None = None,
        mode: str = "qa",   # qa | validation | range
        top_k: int = 5
    ) -> dict:
        try:
            raw_docs = await self._field_specific_search(
                query=query,
                product_type=product_type,
                field_key=field_key,
                top_k=top_k
            )

            facts = self._normalize_docs(raw_docs)
            facts = self._reduce_to_valid_facts(facts)
            grouped = self._group_by_product_and_model(facts)

            return {
                "raw_docs": raw_docs,
                "facts": facts,             
                "grouped": grouped,
            }

        except Exception as err:
            raise RuntimeError("Error during RAG retrieval", err) from err

    async def _semantic_search(
        self,
        query: str,
        product_type: str | None,
        field_key: str | None,
        top_k: int
    ) -> list[dict]:
        try:
            print("product_type:", product_type, field_key)
            print("query:", query)
            q = product_type + " " + query + " " + field_key
            print("q", q)
            embedding = self.embedder.embed_text(q)

            sql = text("""
                SELECT chunk, metadata, product_type, model
                FROM technical_docs
                WHERE (
                    CAST(:product_type AS text) IS NULL
                    OR product_type = CAST(:product_type AS text)
                )
                AND (
                    CAST(:field_key AS text) IS NULL
                    OR metadata->>'field_key' = CAST(:field_key AS text)
                )
                ORDER BY
                    CASE WHEN :field_key IS NULL THEN embedding <=> CAST(:embedding AS vector) END
                LIMIT :top_k
            """)

            params = {
                "embedding": embedding,
                "product_type": product_type,
                "field_key": field_key,
                "top_k": top_k
            }

            with self.db.engine.connect() as conn:
                rows = conn.execute(sql, params).mappings().all()

            print(" lenght of rows", len(rows))
            results = []
            for r in rows:
                metadata = r["metadata"]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)

                results.append({
                    "raw_text": r["chunk"],
                    "product_type": r["product_type"],
                    "model": r["model"],
                    "metadata": metadata
                })
            return results

        except SQLAlchemyError as err:
            raise RuntimeError(
                "Database error during semantic retrieval", err) from err

    async def _field_specific_search(
        self,
        query: str,
        product_type: str | None,
        field_key: str | None,
        top_k: int
    ) -> list[dict]:
        try:
            print("product_type:", product_type, field_key)
            print("query:", query)
            q = product_type + " " + query + " " + field_key
            print("q", q)
            embedding = self.embedder.embed_text(q)

            sql = text("""
                SELECT chunk, metadata, product_type, model
                FROM technical_docs
                WHERE (
                    CAST(:product_type AS text) IS NULL
                    OR product_type = CAST(:product_type AS text)
                )
                AND (
                    CAST(:field_key AS text) IS NULL
                    OR metadata->>'field_key' = CAST(:field_key AS text)
                )
                ORDER BY
                    CASE WHEN :field_key IS NULL THEN embedding <=> CAST(:embedding AS vector) END
                LIMIT :top_k
            """)

            params = {
                "embedding": embedding,
                "product_type": product_type,
                "field_key": field_key,
                "top_k": top_k
            }

            with self.db.engine.connect() as conn:
                rows = conn.execute(sql, params).mappings().all()

            print(" lenght of rows", len(rows))
            results = []
            for r in rows:
                metadata = r["metadata"]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)

                results.append({
                    "raw_text": r["chunk"],
                    "product_type": r["product_type"],
                    "model": r["model"],
                    "metadata": metadata
                })
            return results

        except SQLAlchemyError as err:
            raise RuntimeError(
                "Database error during semantic retrieval", err) from err

    def _normalize_docs(self, docs: list[dict]) -> list[dict]:
        normalized = []

        for d in docs:
            meta = d["metadata"]
            text = d["raw_text"]
            model = d["model"]
            product_type = d["product_type"]

            normalized.append({
                "product_type": product_type,
                "model": model,
                "field_key": meta.get("field_key"),
                "field_type": meta.get("field_type"),
                "value": meta.get("numeric_value") or meta.get("text_value"),
                "unit": meta.get("unit"),
                "source_url": meta.get("source_url"),
                "brochure_url": meta.get("brochure_url"),
            })

        return normalized

    def _reduce_to_valid_facts(self, facts: list[dict]) -> list[dict]:
        reduced = []

        for f in facts:
            if f["value"] in (None, "—", "-", ""):
                continue
            reduced.append(f)

        return reduced

    def _group_by_product_and_model(self, facts: list[dict]) -> dict:
        """
        product_type → model → list of specs
        """
        grouped = defaultdict(lambda: defaultdict(list))

        for f in facts:
            grouped[f["product_type"]][f["model"]].append({
                "field": f["field_key"],
                "value": f["value"],
                "unit": f["unit"],
                "field_type": f["field_type"],
                "source_url": f["source_url"],
            })

        return grouped
