from app.rag.retriever import RAGRetriever
from typing import Any

class RAGValueValidator:
    """
    Performs semantic validation using RAG (pgvector).
    Ensures user input does not exceed known technical limits.
    """

    def __init__(self, retriever: RAGRetriever):
        self.retriever = retriever

    def validate(
        self,
        product: str,
        field: str,
        value: Any
    ) -> tuple[bool, str | None]:
        try:
            # Try numeric conversion once
            try:
                numeric_value = float(value)
            except Exception:
                # Can't validate non-numeric values at RAG level
                return True, None

            docs = self.retriever.retrieve(
                query=f"{product} {field}",
                product_type=product,
                top_k=3,
                field_key=field,
                mode="validation",
            )

            if not docs:
                return True, None

            for doc in docs:
                meta = doc.get("metadata", {})

                # Match exact field
                if meta.get("field_key") != field:
                    continue

                rag_numeric = meta.get("numeric_value")
                if rag_numeric is None:
                    continue

                try:
                    rag_numeric = float(rag_numeric)
                except Exception:
                    continue

                # Core validation rule
                if numeric_value > rag_numeric:
                    unit = meta.get("unit", "")
                    return (
                        False,
                        f"{field} exceeds supported value {rag_numeric} {unit}".strip()
                    )

            return True, None

        except Exception as e:
            raise RuntimeError(
                f"RAG validation failed for product={product}, field={field}"
            ) from e

