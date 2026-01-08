class FieldRangeResolver:
    """
    Resolves valid ranges and nearest acceptable values from RAG data.
    """

    @staticmethod
    def extract_numeric_values(docs, field):
        return [
            d["metadata"]["numeric_value"]
            for d in docs
            if d["metadata"].get("field_key") == field
            and d["metadata"].get("numeric_value") is not None
        ]

    @classmethod
    def get_range(self, docs, field):
        values = self.extract_numeric_values(docs, field)
        if not values:
            return None
        return min(values), max(values)

    @classmethod
    def snap(self, docs, field, user_value):
        values = self.extract_numeric_values(docs, field)
        if not values:
            return None
        return min(values, key=lambda v: abs(v - user_value))