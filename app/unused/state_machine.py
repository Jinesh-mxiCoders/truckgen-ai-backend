# from app.conversation.state.states import ConversationStage, ProductType
# from app.conversation.state.spec_templates import PRODUCT_SPEC_TEMPLATES
# from app.conversation.prompts import WELCOME_MESSAGE, PRODUCT_QUESTIONS, PRODUCT_CONFIRMATION
# from app.conversation.validator import validate
# from app.rag.retriever import RAGRetriever
# from app.rag.context_builder import RAGContextBuilder
# from app.rag.technical_validator import validate_with_rag
# from fastapi import HTTPException
# from app.conversation.run_trun_agent import run_turn_agent


# def _next_missing_field(product: ProductType, data: dict) -> str | None:
#     for field in PRODUCT_SPEC_TEMPLATES[product]:
#         if field not in data:
#             return field
#     return None


# def process_user_message(session: dict, user_message: str) -> tuple[str, bool]:
#     try:
#         # print("session in process_user_message", session)
#         stage = session["stage"]
#         product = session.get("product")
#         data = session.get("data", {})
#         current_field = session.get("current_field")

#         # -----------------------------
#         # 1. WELCOME
#         # -----------------------------
#         if stage == ConversationStage.WELCOME:
#             session["stage"] = ConversationStage.PRODUCT_SELECTION
#             return WELCOME_MESSAGE, False
        
#         # -----------------------------
#         # 2. PRODUCT SELECTION
#         # -----------------------------
#         if stage == ConversationStage.PRODUCT_SELECTION:
#             normalized = user_message.lower()
#             mapping = {
#                 "boom": ProductType.BOOM_PUMP,
#                 "stationary": ProductType.STATIONARY_PUMP,
#                 "placing": ProductType.PLACING_BOOM,
#                 "loop": ProductType.LOOP_BELT
#             }

#             for key, product in mapping.items():
#                 if key in normalized:
#                     session["product"] = product
#                     session["stage"] = ConversationStage.REQUIREMENT_COLLECTION
#                     session["current_field"] = None
#                     return PRODUCT_CONFIRMATION.format(product=product.value.replace("_", " ").title()), False

#             return "Please select one of the listed product categories.", False


#         # -----------------------------
#         # 3. REQUIREMENT COLLECTION
#         # -----------------------------
#         if stage == ConversationStage.REQUIREMENT_COLLECTION:
#             product = session["product"]
#             data = session["data"]

#             # Determine current field
#             if current_field is None:
#                 next_field = _next_missing_field(product, data)
#                 if next_field is None:
#                     session["stage"] = ConversationStage.COMPLETE
#                     return "All requirements collected. Ready to generate the image.", True

#                 session["current_field"] = next_field
#                 return PRODUCT_QUESTIONS[product][next_field], False


#             # -----------------------------
#             # RAG CONTEXT (READ-ONLY)
#             # -----------------------------
#             rag_docs = []
#             if product:
#                 rag_docs = RAGRetriever().retrieve(
#                     query=user_message,
#                     product_type=product,
#                     top_k=5
#                 )

#             rag_context = RAGContextBuilder.build(rag_docs)
#             print("rag_context", rag_context)

#             # -------------------------------------------------
#             # SINGLE LLM TURN (DECISION MAKER)
#             # -------------------------------------------------
#             agent_output = run_turn_agent(
#                 stage=stage,
#                 product=product,
#                 current_field=current_field,
#                 data=data,
#                 user_message=user_message,
#                 rag_context=rag_context
#             )

#             print("agent_output", agent_output)

#             intent = agent_output["intent"]

#             # -------------------------------------------------
#             # USER ASKED A QUESTION → ANSWER & STAY ON FIELD
#             # -------------------------------------------------
#             if intent == "ANSWER_USER_QUESTION":
#                 return agent_output["reply"], False

#             # -------------------------------------------------
#             # NEED CLARIFICATION
#             # -------------------------------------------------
#             if intent == "CLARIFY":
#                 return agent_output["reply"], False

#             # -------------------------------------------------
#             # INVALID / SAFETY FALLBACK
#             # -------------------------------------------------
#             if intent == "INVALID":
#                 return agent_output["reply"], False

#             # -------------------------------------------------
#             # ANSWER FIELD (STRICT PATH)
#             # -------------------------------------------------
#             if intent == "ANSWER_FIELD":
#                 field = agent_output["field"]
#                 value = agent_output["value"]

#                 if field != current_field:
#                     return f"Please answer the current question: {PRODUCT_QUESTIONS[product][current_field]}", False

#                 # Local validation
#                 valid, error = validate(field, value)
#                 if not valid:
#                     return f"{error} {PRODUCT_QUESTIONS[product][field]}", False

#                 # RAG validation
#                 rag_valid, rag_error = validate_with_rag(
#                     product=product.value,
#                     field=field,
#                     value=value
#                 )
#                 if not rag_valid:
#                     return f"{rag_error} {PRODUCT_QUESTIONS[product][field]}", False

#                 # Store
#                 data[field] = value
#                 session["current_field"] = None

#                 # Ask next or complete
#                 next_field = _next_missing_field(product, data)
#                 if next_field:
#                     session["current_field"] = next_field
#                     return PRODUCT_QUESTIONS[product][next_field], False

#                 session["stage"] = ConversationStage.COMPLETE
#                 return "All requirements collected. Ready to generate the image.", True

#         # =====================================================
#         # 4. COMPLETE
#         # =====================================================
#         return "Configuration complete. You may now proceed.", True

#     except Exception as e:
#         print("CHAT ERROR:", repr(e))
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error while processing chat"
#         )