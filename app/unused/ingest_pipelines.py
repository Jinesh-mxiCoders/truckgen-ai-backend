import json
import re
from sqlalchemy import text
from app.core.database import Database
from app.rag.embeddings import EmbeddingGenerator

CATEGORY_MAP = {
    "Boom Pumps": "boom_pump",
    "Stationary Pumps": "stationary_pump",
    "Placing Booms": "placing_boom",
    "Loop Belts": "loop_belt"
}

embedder = EmbeddingGenerator()

db = Database()

def parse_numeric_and_unit(value: str):
    """
    Extract numeric value AND unit from a spec string.

    Examples:
      '113′ 8″'          -> (113.0, "ft-in")
      '8.40 cu-yd/min'   -> (8.40, "cu-yd/min")
      '145 cu yds/h'     -> (145.0, "cu yds/h")
    """
    if not value:
        return None, None

    num_match = re.search(r"[\d.]+", value.replace(",", ""))
    numeric_value = float(num_match.group()) if num_match else None

    # Remove numeric part to get unit
    unit = value.replace(num_match.group(), "").strip() if num_match else None

    return numeric_value, unit



def build_embedding_text(spec_row: dict) -> str:
    """
    Build semantically correct embedding text.
    Always preserve original value + unit relationship.
    """
    return (
        f"{spec_row['product_type']} model {spec_row['model']} "
        f"{spec_row['field_key']} is {spec_row['raw_text']}"
    )


def upsert_embedding(
    product_type: str,
    model: str | None,
    text_chunk: str,
    metadata: dict,
    embedding: list[float]
):
    """
    Insert or update embedding in PostgreSQL.
    Assumes table 'technical_docs' exists with pgvector column 'embedding'.
    """
    with db.engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO technical_docs (product_type, model, chunk, metadata, embedding)
                VALUES (:product_type, :model, :chunk, :metadata, :embedding)
                ON CONFLICT (product_type, model, chunk) 
                DO UPDATE SET metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding
            """),
            {
                "product_type": product_type,
                "model": model,
                "chunk": text_chunk,
                "metadata": json.dumps(metadata),
                "embedding": embedding
            }
        )


def normalize_product(item: dict) -> list[dict]:
    """
    Convert your JSON product into a list of specification rows.
    """
    product_type = CATEGORY_MAP.get(item["category"], "other")
    model = item["name"]
    rows = []

    print("Processing product:", model, product_type)

    for raw_field, raw_value in item["specifications"].items():
        numeric_value, unit = parse_numeric_and_unit(raw_value)
        field_type = "number" if numeric_value is not None else "text"

        print(" sepc:", raw_field, "->", raw_value)

        rows.append({
            "product_type": product_type,
            "model": model,
            "field_key": raw_field,
            "field_type": field_type,
            "unit": unit,  
            "numeric_value": numeric_value,
            "text_value": raw_value,
            "raw_text": raw_value
        })

    return rows


def ingest_json_file(json_path: str):
    """
    Main function to ingest your JSON file into PostgreSQL vector DB.
    """

    print("Ingesting JSON file", json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    print("Loaded", len(items), "products from JSON")

    for item in items:
        rows = normalize_product(item)
        chunks = [build_embedding_text(row) for row in rows]
        print("Generating embedding for", len(chunks), "chunks...")
        embeddings = embedder.embed_documents(chunks)

        for row, chunk, embedding in zip(rows, chunks, embeddings):
            print("inserting chunks")
            print(chunk)
            print("embedding")
            print(embedding[:5])
            upsert_embedding(
                product_type=row["product_type"],
                model=row["model"],
                text_chunk=chunk,
                metadata={
                    "field_key": row["field_key"],
                    "field_type": row["field_type"],
                    "unit": row["unit"],
                    "numeric_value": row["numeric_value"],
                    "text_value": row["text_value"],
                    "raw_text": row["raw_text"],
                    "source_url": item.get("source_url"),
                    "brochure_url": item.get("brochure_url")
                },
                embedding=embedding
            )