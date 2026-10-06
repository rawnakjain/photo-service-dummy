import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from controllers.service_extraction_controller import ServiceExtractionController
from models.service_models import ServiceExtractionResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache(maxsize=1)
def get_controller() -> ServiceExtractionController:
    """Build the controller on first request.

    Deferred rather than module-level so that importing this module (for tests, for
    OpenAPI generation) does not require a Gemini API key or a database.
    """
    return ServiceExtractionController()


@router.post("/extract-services", response_model=ServiceExtractionResponse)
async def extract_services(
    file: UploadFile = File(..., description="Salon menu image file"),
    salon_id: str | None = None,
    controller: ServiceExtractionController = Depends(get_controller),
):
    """Extract salon services from an uploaded menu image and match them to the catalog."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty upload")

    try:
        return await controller.extract_services_from_image(
            image_data=content,
            filename=file.filename or "upload",
            salon_id=salon_id,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller as a 500
        logger.exception("Error processing image %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {exc}",
        ) from exc


@router.get("/health")
async def health_check():
    """Liveness for this router's mount point."""
    return {"status": "healthy", "service": "service-extraction"}
