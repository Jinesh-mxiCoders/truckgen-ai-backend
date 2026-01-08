# import json
# from app.core.llm import llm_client


# SYSTEM_PROMPT = """
#     You are an AI assistant that extracts structured values from user input.

#     Rules:
#     - Do NOT guess.
#     - Do NOT infer missing units.
#     - If unclear, return null.
#     - Output ONLY valid JSON.
#     """

# FIELD_TYPE_RULES = {
#     "number": "Return a numeric value only.",
#     "enum": "Return one of the allowed values exactly."
# }


# def extract_value(field: str, user_message: str) -> dict:
#     prompt = f"""
# Field: {field}

# Expected type:
# - numeric if contains _m, _bar, _m3_hr
# - enum otherwise

# User input:
# "{user_message}"

# Rules:
# - Do not infer missing units
# - Do not guess ranges

# Return JSON:
# {{
#   "value": <parsed value or null>,
#   "confidence": "high" | "low"
# }}
# """

#     raw = llm_client.call_llm(SYSTEM_PROMPT, prompt)

#     print("raw",raw)

#     try:
#         return json.loads(raw)
#     except json.JSONDecodeError:
#         return {"value": None, "confidence": "low"}
