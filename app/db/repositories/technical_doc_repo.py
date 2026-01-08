from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.technical_doc import TechnicalDoc

class TechnicalDocRepository:
    def __init__(self, session: Session):
        self.session = session

    def semantic_search(
        self,
        embedding: list[float],
        product_type: Optional[str] = None,
        field_key: Optional[str] = None,
        top_k: int = 5,
    ) -> List[TechnicalDoc]:
        """
        Single source of truth for semantic queries.
        Easy to extend with conditions.
        """

        stmt = (
            select(TechnicalDoc)
            .order_by(TechnicalDoc.embedding.l2_distance(embedding))
            .limit(top_k)
        )

        if product_type:
            stmt = stmt.where(TechnicalDoc.product_type == product_type)

        if field_key:
            stmt = stmt.where(
                TechnicalDoc.metadata["field_key"].astext == field_key
            )

        return self.session.execute(stmt).scalars().all()
