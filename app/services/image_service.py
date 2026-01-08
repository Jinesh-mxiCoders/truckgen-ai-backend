from app.rag.data.truck_model_images import TRUCK_MODEL_IMAGES
from app.image_engine.prompt_builder import ImagePromptBuilder
from app.schemas.image import ImageGenerationRequest, ImageGenerationResult
from config import settings

class ImageService:
    def __init__(self):
        self.model_images = TRUCK_MODEL_IMAGES
        self.prompt_builder = ImagePromptBuilder()

    def get_images(self, model: str) -> list[str]:
        """Return all images for a model (empty list if not found)."""
        paths = self.model_images.get(model, [])    
        return [f"{settings.BASE_URL}{path}" for path in paths]

    def get_primary_image(self, model: str) -> str | None:
        """Return the primary (0th index) image for a model."""
    
        images = self.get_images(model)
        return images[0] if images else None
    
    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        prompt = self.prompt_builder.build_prompt(
            category=request.category,
            model_name=request.model_name,
            specifications=request.specifications,
            user_prompt=request.user_prompt,
        )

        image_url=""
        # image_url = self.provider.generate_image(
        #     prompt=prompt,
        #     negative_prompt=self.prompt_builder.NEGATIVE_PROMPT
        # )

        return ImageGenerationResult(
            model_name=request.model_name,
            image_url=image_url,
            prompt_used=prompt
        )
