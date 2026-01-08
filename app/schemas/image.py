from typing import Dict, Optional
from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    category: str
    model_name: str
    specifications: Dict[str, str]
    user_prompt: Optional[str] = None


class ImageGenerationResult(BaseModel):
    model_name: str
    image_url: str
    prompt_used: str
