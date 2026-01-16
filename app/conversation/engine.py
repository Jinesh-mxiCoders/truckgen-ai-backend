from fastapi import HTTPException
from app.conversation.state.states import ConversationStage, ProductType
from app.conversation.state.spec_templates import PRODUCT_SPEC_TEMPLATES
from app.conversation.chatbot_prompts import (
    WELCOME_MESSAGE,
    PRODUCT_QUESTIONS,
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

    # -------------------------------
    # Product keyword definitions
    # -------------------------------
    PRODUCT_KEYWORDS = {
        ProductType.PLACING_BOOM: ["placing boom", "placing booms", "boom placer", "boom placing", "plcing boom", "placing-bom"],
        ProductType.BOOM_PUMP: ["boom pump", "boom", "booms", "boom pumps","boom-pump", "bump", "boomp",],
        ProductType.STATIONARY_PUMP: ["stationary pump", "stationary pumps", "stationary", "stat pump", "fixed pump", "immobile pump"],
        ProductType.LOOP_BELT: ["loop belt", "loop", "loop belts", "belt loop", "belt", "belt conveyor", "conveyor loop","loop conveyor"],
    }

    def __init__(self):
        self.retriever = retriever
        self.field_constraint_validator = field_constraint_validator
        self.rag_validator = rag_validator
        self.PRODUCT_PATTERNS = self._build_product_patterns()

    # -------------------------------
    # Utilities
    # -------------------------------
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize user input for consistent matching."""
        return re.sub(r"\s+", " ", text.lower().strip())

    def _build_product_patterns(self):
        """
        Build regex patterns for all products.
        Sorted by longest phrase first (more specific matches first)
        """
        patterns = []
        for product, phrases in self.PRODUCT_KEYWORDS.items():
            for phrase in phrases:
                escaped = re.escape(phrase).replace(r"\ ", r"\s+")
                patterns.append((product, rf"\b{escaped}\b", len(phrase)))
        patterns.sort(key=lambda x: x[2], reverse=True)
        return patterns

    def detect_product(self, user_message: str):
        """Detect product from user message using patterns."""
        normalized = self._normalize_text(user_message)
        for product, pattern, _ in self.PRODUCT_PATTERNS:
            if re.search(pattern, normalized):
                return product
        return None

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
                product = self.detect_product(user_message)

                if product:
                    session["product"] = product
                    session["stage"] = ConversationStage.REQUIREMENT_COLLECTION
                    session["data"] = {}

                    next_field = self._next_missing_field(product, {})
                    session["current_field"] = next_field
                    return EngineResponse(
                        action=EngineAction.ASK,
                        message=PRODUCT_QUESTIONS[product][next_field],
                        payload={ "product": product.value }
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
                                top_k=3
                            )

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

                # ---- RAG (read only) ----
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

                if intent in {"ANSWER_USER_QUESTION", "CLARIFY", "INVALID", "ASK_QUESTION"}:
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
                    
                    else:
                        session["stage"] = ConversationStage.MODEL_RECOMMENDATION
                        recommendations = ModelMatchResolver().resolve(
                                collected_data=session["data"],
                                top_k=3
                            )

                        print("recommendations", recommendations)
                        return EngineResponse(
                            action=EngineAction.MODEL_RECOMMENDATION,
                            message=f"Based on your inputs, here are the recommended {session['product']} models. You can review and compare their specifications in the table below. Please type the model name to view images.",
                            payload=recommendations
                        )


            # =====================================================
            # 4. MODEL RECOMMENDATION if not recommend
            # =====================================================
            if session["stage"] == ConversationStage.MODEL_RECOMMENDATION and not session.get("recommend_models"):
                print("model recommneding.......")
                recommendations = ModelMatchResolver().resolve(
                    collected_data=session["data"],
                    top_k=3
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

conversation_engine = ConversationEngine()
