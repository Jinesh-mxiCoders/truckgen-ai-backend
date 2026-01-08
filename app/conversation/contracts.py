from enum import Enum
from typing import Any, Optional


class EngineAction(str, Enum):
    ASK = "ask"
    REPLY= "reply"
    WELCOME="welcome"
    PRODUCT_SELECTION="product_selection"
    COMPLETE = "complete"
    MODEL_RECOMMENDATION = "model_recommendation",
    MODEL_SELECTED = "model_selected",
    INVALID = "invalid"
    ERROR = "error"



class EngineResponse:
    def __init__(
        self,
        *,
        action: EngineAction,
        message: Optional[str] = None,
        payload: Optional[Any] = None,
    ):
        self.action = action
        self.message = message
        self.payload = payload

    def __repr__(self):
        return (
            f"EngineResponse(action={self.action}, "
            f"message={self.message}, "
            f"payload={self.payload}, "
        )