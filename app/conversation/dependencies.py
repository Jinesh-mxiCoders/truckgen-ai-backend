from app.core.database import Database
from app.rag.embeddings import EmbeddingGenerator
from app.rag.retriever import RAGRetriever
from app.conversation.validators.field_constraint_validator import (
    FieldConstraintValidator,
)
from app.conversation.validators.rag_validator import RAGValueValidator


db = Database()
embedder = EmbeddingGenerator()
retriever = RAGRetriever(db, embedder)


field_constraint_validator = FieldConstraintValidator()
rag_validator = RAGValueValidator(retriever)
