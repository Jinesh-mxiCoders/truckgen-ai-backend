from enum import Enum

class ConversationStage(str, Enum):
    WELCOME = "welcome"
    PRODUCT_SELECTION = "product_selection"
    REQUIREMENT_COLLECTION = "requirement_collection"
    MODEL_RECOMMENDATION = "model_recommendation",
    MODEL_SELECTED = "model_selected"
    VALIDATION = "validation"
    COMPLETE = "complete"


class ProductType(str, Enum):
    BOOM_PUMP = "boom_pump"
    STATIONARY_PUMP = "stationary_pump"
    PLACING_BOOM = "placing_boom"
    LOOP_BELT = "loop_belt"
