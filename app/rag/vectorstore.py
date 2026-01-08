from sqlalchemy import text
from app.core.database import Database

EMBEDDING_DIM = 768

class VectorStore:
    """
    Responsible for initializing the PGVector table and index.
    This should run once on app startup.
    """

    def __init__(self, db: Database):
        self.db = db

    def init_pgvector(self):
        """
        Create the technical_docs table, unique constraints, and IVFFlat index if not exists.
        """
        try:
            with self.db.engine.begin() as conn:
                vector_exists = conn.execute(
                    text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector')")
                ).scalar()

                if not vector_exists:
                    print("⚠️ pgvector extension is NOT enabled.")
                    return

                print("✅ pgvector extension is enabled and ready to use.")

                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS technical_docs (
                        id SERIAL PRIMARY KEY,
                        product_type TEXT NOT NULL,
                        model TEXT,
                        chunk TEXT NOT NULL,
                        metadata JSONB,
                        embedding VECTOR({EMBEDDING_DIM})
                    );
                """))

                conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1
                            FROM information_schema.table_constraints
                            WHERE constraint_name = 'unique_product_chunk'
                              AND table_name = 'technical_docs'
                        ) THEN
                            ALTER TABLE technical_docs
                            ADD CONSTRAINT unique_product_chunk
                            UNIQUE (product_type, model, chunk);
                        END IF;
                    END$$;
                """))

                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS technical_docs_embedding_idx
                    ON technical_docs
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """))

                print("✅ technical_docs table is ready with unique constraint and IVFFlat index.")

        except Exception as e:
            print(f"❌ Failed to initialize vector table: {e}")

vector_store = VectorStore(Database())