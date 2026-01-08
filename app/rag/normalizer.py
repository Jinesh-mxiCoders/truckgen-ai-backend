import re
from app.rag.field_registry import CATEGORY_MAP

class ProductNormalizer:
    """
    Normalize raw JSON product specs into structured rows suitable for embedding.
    """

    @staticmethod
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

    def normalize_product(self, item: dict) -> list[dict]:
        """
        Convert your JSON product into a list of specification rows.
        """
        product_type = CATEGORY_MAP.get(item.get("category"), "other")
        model = item.get("name")
        rows = []

        print("Processing product:", model, product_type)

        for raw_field, raw_value in item.get("specifications", {}).items():
            numeric_value, unit = self.parse_numeric_and_unit(raw_value)
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
