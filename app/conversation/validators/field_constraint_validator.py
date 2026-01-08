from typing import Any

class FieldConstraintValidator:
    """
    Validates local field constraints (type, presence, numeric bounds).
    Does NOT rely on external knowledge or RAG.
    """

    NUMERIC_SUFFIXES = ("_m", "_m3_hr", "_bar")

    def validate(self, field: str, value: Any) -> tuple[bool, str | None]:
        try:
            # Only numeric-like fields need checking
            if not field.endswith(self.NUMERIC_SUFFIXES):
                return True, None

            if value is None:
                return False, "Value is required."

            if isinstance(value, (int, float)):
                if value <= 0:
                    return False, "Value must be greater than zero."
                return True, None

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return False, "Value is required."

                try:
                    numeric = float(value)
                except Exception:
                    return False, "Numeric value expected."

                if numeric <= 0:
                    return False, "Value must be greater than zero."

                return True, None

            return False, "Numeric value expected."

        except Exception:
            return False, "Invalid value."

field_constraint_validator = FieldConstraintValidator()