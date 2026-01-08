from sqlalchemy import Column, Integer, String, Text, JSON
from pgvector.sqlalchemy import VECTOR
from core.database import Base

EMBEDDING_DIM = 768

class TechnicalDoc(Base):
    __tablename__ = "technical_docs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_type = Column(String, nullable=False)
    model = Column(String, nullable=True)
    chunk = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    embedding = Column(VECTOR(EMBEDDING_DIM))
    
    def __repr__(self):
        return f"<TechnicalDoc(id={self.id}, product_type={self.product_type}, chunk={self.chunk[:50]}...)>"
