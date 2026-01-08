from fastapi import HTTPException
from app.conversation.state.states import ConversationStage, ProductType
from app.conversation.state.spec_templates import PRODUCT_SPEC_TEMPLATES
from app.conversation.prompts import (
    WELCOME_MESSAGE,
    PRODUCT_QUESTIONS,
    PRODUCT_CONFIRMATION,
)
from app.rag.context_builder import RAGContextBuilder
from app.conversation.dependencies import (
    retriever,
    field_constraint_validator,
    rag_validator,
)
from app.conversation.nlu.turn_intent_interpreter import TurnIntentInterpreter
from app.services.model_match_resolver import ModelMatchResolver
from app.conversation.contracts import EngineResponse, EngineAction
import re


class ConversationEngine:
    """
    Orchestrates conversation flow and state transitions.
    """

    def __init__(self):
        self.retriever = retriever
        self.field_constraint_validator = field_constraint_validator
        self.rag_validator = rag_validator

    def _next_missing_field(self, product: ProductType, data: dict) -> str | None:
        for field in PRODUCT_SPEC_TEMPLATES[product]:
            if field not in data:
                return field
        return None

    async def process(self, session: dict, user_message: str) -> tuple[str, bool]:
        try:
            stage = session["stage"]
            product = session.get("product", None)
            data = session.get("data", {})
            current_field = session.get("current_field", None)

            # -----------------------------
            # 1. WELCOME
            # -----------------------------
            if stage == ConversationStage.WELCOME:
                # session["stage"] = ConversationStage.PRODUCT_SELECTION
                print("welcome")
                return EngineResponse(
                    action=EngineAction.WELCOME,
                    message=WELCOME_MESSAGE
                )

            # -----------------------------
            # 2. PRODUCT SELECTION
            # -----------------------------
            if stage == ConversationStage.PRODUCT_SELECTION:
                normalized = user_message.lower()
                mapping = {
                    "boom": ProductType.BOOM_PUMP,
                    "stationary": ProductType.STATIONARY_PUMP,
                    "placing": ProductType.PLACING_BOOM,
                    "loop": ProductType.LOOP_BELT,
                }

                for key, prod in mapping.items():
                    if key in normalized:
                        session["product"] = prod
                        session["stage"] = ConversationStage.REQUIREMENT_COLLECTION
                        session["data"] = {}

                        next_field = self._next_missing_field(prod, {})
                        session["current_field"] = next_field
                        return EngineResponse(
                            action=EngineAction.ASK,
                            message=PRODUCT_QUESTIONS[prod][next_field],
                            payload={
                                "product": prod.value
                            }
                        )
                    
                return EngineResponse(
                    action=EngineAction.ASK,
                    message="Please select one of the products listed above",
                    payload={}
                )

            # -----------------------------
            # 3. REQUIREMENT COLLECTION
            # -----------------------------
            if stage == ConversationStage.REQUIREMENT_COLLECTION:
                current_field = session["current_field"]
                if current_field is None:
                    next_field = self._next_missing_field(product, data)
                    if not next_field:
                        session["stage"] = ConversationStage.MODEL_RECOMMENDATION
                        recommendations = ModelMatchResolver().resolve(
                                collected_data=session["data"],
                                top_k=5
                            )

                        print("recommendations", recommendations)
                        return EngineResponse(
                            action=EngineAction.MODEL_RECOMMENDATION,
                            message=f"Based on your inputs, here are the recommended {session['product']} models. You can review and compare their specifications in the table below. Please type the model name to view images.",
                            payload=recommendations
                        )

                    session["current_field"] = next_field
                    return EngineResponse(
                        action=EngineAction.ASK,
                        message=PRODUCT_QUESTIONS[product][next_field]
                    )

                # ---- RAG (read-only) ----
                retrieval_result = await self.retriever.retrieve_constraint_fields(
                    query=user_message,
                    product_type=product,
                    field_key=current_field,
                    top_k=200,
                )

                # print("retrival grouped: ", retrieval_result.get("grouped", {}))

                rag_context = RAGContextBuilder._build_llm_context(
                    grouped=retrieval_result.get("grouped", {}))
                print("llm rag_context")
                print(rag_context)

                agent_output = TurnIntentInterpreter().interpret(
                    stage=stage,
                    product=product,
                    current_field=current_field,
                    questions = PRODUCT_QUESTIONS[product][current_field],
                    data=data,
                    user_message=user_message,
                    rag_context=rag_context,
                )
                print("agent_output", agent_output)

                intent = agent_output["intent"]

                if intent in {"ANSWER_USER_QUESTION", "CLARIFY", "INVALID"}:
                    return EngineResponse(
                        action=EngineAction.REPLY,
                        message=agent_output["reply"]
                    )

                if intent == "ANSWER_FIELD":
                    field = agent_output["field"]
                    value = agent_output["value"]
                    unit = agent_output.get("unit")
                    matched_models = agent_output.get("matched_model", [])

                    if field not in data:
                        data[field] = {
                            "value": None,
                            "unit": None,
                            "matched_models": []
                        }

                    if field != current_field:
                        return EngineResponse(
                            action=EngineAction.ASK,
                            message=PRODUCT_QUESTIONS[product][current_field]
                        )

                    # Store normalized value
                    data[field]["value"] = value
                    data[field]["unit"] = unit
                    if isinstance(matched_models, list):
                        data[field]["matched_models"] = matched_models
                    else:
                        data[field]["matched_models"] = []

                    print("data", data)

                    # Clear current field to move forward
                    session["current_field"] = None

                    # Ask next or complete
                    next_field = self._next_missing_field(product, data)
                    if next_field:
                        session["current_field"] = next_field
                        return EngineResponse(
                            action=EngineAction.ASK,
                            message=PRODUCT_QUESTIONS[product][next_field]
                        )

            # =====================================================
            # 4. MODEL RECOMMENDATION if not recommend
            # =====================================================
            if session["stage"] == ConversationStage.MODEL_RECOMMENDATION and not session.get("recommend_models"):
                print("model recommneding.......")
                recommendations = ModelMatchResolver().resolve(
                    collected_data=session["data"],
                    top_k=5
                )

                return EngineResponse(
                    action=EngineAction.MODEL_RECOMMENDATION,
                    message=f"Based on your inputs, here are the recommended {session['product']} models. You can review and compare their specifications in the table below. Please type the model name to view images.",
                    payload=recommendations
                )

            # =====================================================
            # 5. MODEL Input validation
            # =====================================================
            elif session["stage"] == ConversationStage.MODEL_RECOMMENDATION and session.get("recommend_models") and not session.get("selected_models"): 
                print("mode input validations.........")    
                message = user_message.strip().lower()
                recommended_models =  session.get("recommend_models", {})
                allowed_models = set(recommended_models.keys())

                selected_model = None

                # Try to extract model name from free-text input
                for model in allowed_models:
                    pattern = re.escape(model.lower())
                    if re.search(pattern, message):
                        selected_model = model
                        break

                if not selected_model:
                    model_list = ", ".join(allowed_models)
                    return EngineResponse(
                        message=f"Please select any one of: {model_list}",
                        action=EngineAction.INVALID
                    )

                print("selected_models", selected_model)
                return EngineResponse(
                    message=f"Showing images for {selected_model}.",
                    action=EngineAction.MODEL_SELECTED,
                    payload={"model": selected_model}
                )

            # =====================================================
            # 6. MODEL SELECTED
            # =====================================================
            if session["stage"] == ConversationStage.MODEL_SELECTED:
                selected_model = session.get("selected_models")
                print("model selected", selected_model)
                return EngineResponse(
                    message=f"Showing images for {selected_model}.",
                    action=EngineAction.MODEL_SELECTED,
                    payload={"model": selected_model}
                )
            
            return EngineResponse(
                    message=f"Thank you",
                    action=EngineAction.COMPLETE,
                )

        except Exception as e:
            print("CONVERSATION ENGINE ERROR:", e)
            raise HTTPException(
                status_code=500,
                detail="Internal server error while processing chat",
            ) from e

    async def process_with_QA(self, session: dict, user_message: str) -> tuple[str, bool]:
        try:
            stage = session["stage"]
            product = session.get("product")
            data = session.get("data", {})
            current_field = session.get("current_field")

            # -----------------------------
            # 1. WELCOME
            # -----------------------------
            if stage == ConversationStage.WELCOME:
                session["stage"] = ConversationStage.PRODUCT_SELECTION
                return WELCOME_MESSAGE, False

            # -----------------------------
            # 2. PRODUCT SELECTION
            # -----------------------------
            if stage == ConversationStage.PRODUCT_SELECTION:
                normalized = user_message.lower()
                mapping = {
                    "boom": ProductType.BOOM_PUMP,
                    "stationary": ProductType.STATIONARY_PUMP,
                    "placing": ProductType.PLACING_BOOM,
                    "loop": ProductType.LOOP_BELT,
                }

                for key, prod in mapping.items():
                    if key in normalized:
                        session["product"] = prod
                        session["stage"] = ConversationStage.REQUIREMENT_COLLECTION
                        session["current_field"] = None

                        next_field = self._next_missing_field(prod, {})
                        session["current_field"] = next_field
                        return PRODUCT_QUESTIONS[prod][next_field], False

                return "Please select one of the listed product categories.", False

            # -----------------------------
            # 3. REQUIREMENT COLLECTION
            # -----------------------------
            if stage == ConversationStage.REQUIREMENT_COLLECTION:
                if current_field is None:
                    next_field = self._next_missing_field(product, data)
                    if not next_field:
                        session["stage"] = ConversationStage.COMPLETE
                        return "All requirements collected. Ready to generate the image.", True

                    session["current_field"] = next_field
                    return PRODUCT_QUESTIONS[product][next_field], False

                # ---- RAG (read-only) ----
                retrieval_result = await self.retriever.retrieve(
                    query=user_message,
                    # product_type=product,
                    field_key=current_field,
                    mode="qa",
                    top_k=200,
                )

                rag_context = RAGContextBuilder._build_llm_context(
                    grouped=retrieval_result.get("grouped", {}))
                print("llm rag_context")
                print(rag_context)

                return 0

                agent_output = TurnIntentInterpreter().interpret(
                    stage=stage,
                    product=product,
                    current_field=current_field,
                    data=data,
                    user_message=user_message,
                    rag_context=rag_context,
                )
                print("agent_output", agent_output)

                intent = agent_output["intent"]

                if intent in {"ANSWER_USER_QUESTION", "CLARIFY", "INVALID"}:
                    return agent_output["reply"], False

                if intent == "ANSWER_FIELD":
                    field = agent_output["field"]
                    value = agent_output["value"]

                    if field != current_field:
                        return PRODUCT_QUESTIONS[product][current_field], False

                    # Basic validation
                    valid, error = self.field_constraint_validator.validate(
                        field, value)
                    if not valid:
                        return f"{error} {PRODUCT_QUESTIONS[product][field]}", False

                    # RAG validation
                    rag_valid, rag_error = self.rag_validator.validate(
                        product=product,
                        field=field,
                        value=value,
                    )
                    if not rag_valid:
                        return f"{rag_error} {PRODUCT_QUESTIONS[product][field]}", False

                    # Save fields in session
                    data[field] = value
                    session["current_field"] = None

                    # Ask next or complete
                    next_field = self._next_missing_field(product, data)
                    if next_field:
                        session["current_field"] = next_field
                        return PRODUCT_QUESTIONS[product][next_field], False

                    session["stage"] = ConversationStage.COMPLETE
                    return "All requirements collected. Ready to generate the image.", True

            # =====================================================
            # 4. COMPLETE
            # =====================================================
            return "Configuration complete.", True

        except Exception as e:
            print("CONVERSATION ENGINE ERROR:", e)
            raise HTTPException(
                status_code=500,
                detail="Internal server error while processing chat",
            ) from e


conversation_engine = ConversationEngine()

# # Basic validation
# valid, error = self.field_constraint_validator.validate(field, value)
# if not valid:
#     return f"{error} {PRODUCT_QUESTIONS[product][field]}", False

# # RAG validation
# rag_valid, rag_error = self.rag_validator.validate(
#     product=product,
#     field=field,
#     value=value,
#     top_k=200,
# )
# if not rag_valid:
#     return f"{rag_error} {PRODUCT_QUESTIONS[product][field]}", False
