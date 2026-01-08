import json
from app.core.llm import llm_client

class TurnIntentInterpreter:
    SYSTEM_PROMPT = """
    You are a constrained industrial product assistant.

    Your job:
    - Guide the user to configure a truck; never skip required fields or invent values.
    - Respect the current conversation stage and required fields.
    - If the user provides an approximate or ranged value, you MUST select the closest valid value from the RAG Context.
    - If no valid or reasonable match exists, ask the user to choose from available options or between range.
    - Answer user questions using RAG context.
    - Respond only in STRICT JSON.

    Allowed intents:
    - ANSWER_FIELD           # User provided a clear value for the required field
    - ANSWER_USER_QUESTION   # Respond to user questions using RAG
    - ASK_QUESTION           # Assistant needs to ask for missing info
    - CLARIFY                # Clarify ambiguous user input
    - INVALID
    """

    def interpret(
        self,
        *,
        stage,
        product,
        current_field,
        questions,
        data: dict,
        user_message: str,
        rag_context: str
    ) -> dict:
        prompt = f"""
        STAGE: {stage}
        PRODUCT: {product}
        QUESTION ASKED TO USER: {questions}
        EXPECTED_FIELD: {current_field}
        COLLECTED DATA: {json.dumps(data, indent=2)}

        RAG Context:
        {rag_context}

        USER INPUT:
        {user_message}

        Respond in STRICT JSON:
        {{
            "intent": "ANSWER_FIELD | ANSWER_USER_QUESTION | ASK_QUESTION | CLARIFY | INVALID",
            "field": null or string,
            "value": null or extracted value,
            "unit": string | null,
            "matched_model": [string] | null,    e.g ["SP 123-45", "SP 678-90"]
            "confidence": "high" or "low",
            "reply": null or string
        }}
        """

        response = llm_client.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        try:
            return json.loads(response)
        except Exception:
            return {
                "intent": "INVALID",
                "field": None,
                "value": None,
                "confidence": "low",
                "reply": "I couldn’t understand that. Could you please clarify?"
            }
