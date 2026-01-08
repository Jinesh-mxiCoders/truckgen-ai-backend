import json


class RAGContextBuilder:
    """
    Converts retrieved documents into LLM-ready context.
    """

    @staticmethod
    def build(docs: list[dict]) -> str:
        if not docs:
            return "No technical reference available."

        blocks = []

        for i, doc in enumerate(docs, start=1):
            block = f"""
Reference {i}:
Text: {doc["raw_text"]}

Metadata:
{json.dumps(doc.get("metadata", {}), indent=2)}
"""
            blocks.append(block.strip())

        return "\n\n".join(blocks)
    
    @staticmethod
    def _build_llm_context(grouped: dict) -> str:
        """
        Builds compact, hallucination-resistant LLM context.
        """
        lines = []

        for product_type, models in grouped.items():
            lines.append(f"Product Type: {product_type.replace('_', ' ').title()}")

            for model, specs in models.items():
                lines.append(f"  Model {model}:")

                for s in specs:
                    if s["unit"]:
                        lines.append(
                            f"    - {s['field']}: {s['value']} {s['unit']}"
                        )
                    else:
                        lines.append(
                            f"    - {s['field']}: {s['value']}"
                        )

            lines.append("")

        return "\n".join(lines)
