import logging
from typing import List, Optional

from fastapi.concurrency import run_in_threadpool

from models.service_models import ServiceExtractionResponse
from services.database_service import DatabaseService
from services.gemini_service import GeminiService, Menu
from utils.normalizers import format_variation_response
from utils.prompt_templates import SALON_MENU_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ServiceExtractionController:
    def __init__(self):
        self._gemini_service: Optional[GeminiService] = None
        self.db_service = DatabaseService()

    @property
    def gemini_service(self) -> GeminiService:
        """Lazily build the Gemini client so construction never needs an API key."""
        if self._gemini_service is None:
            self._gemini_service = GeminiService()
        return self._gemini_service

    async def extract_services_from_image(
        self, image_data: bytes, filename: str, salon_id: Optional[str] = None
    ) -> ServiceExtractionResponse:
        """Extract the menu from an image, then match it against the service catalog."""
        logger.info("Processing image: %s", filename)

        extracted_menu = await self.gemini_service.extract_menu_from_image(
            image_data=image_data, prompt=SALON_MENU_EXTRACTION_PROMPT
        )
        logger.info("Extracted %d categories from image", len(extracted_menu.categories))

        matched = await self._match_services_with_database(extracted_menu, salon_id)
        logger.info("Matched %d variations", len(matched))

        return ServiceExtractionResponse(
            success=True,
            data=matched,
            metadata={
                "processed_image": filename,
                "categories_found": len(extracted_menu.categories),
                "total_variations_matched": len(matched),
                "salon_id": salon_id,
            },
        )

    async def _match_services_with_database(
        self, extracted_menu: Menu, salon_id: Optional[str] = None
    ) -> List[dict]:
        """Resolve each extracted service to known variations.

        Strategy per service: exact/partial name match against the ``services`` catalog
        first; if that finds nothing, fall back to a text search over
        ``variationnameandserviceid``. Results are flattened and deduplicated — a menu
        that lists the same service under two headings should not yield two identical rows.
        """
        matched: List[dict] = []
        seen_variation_ids: set[str] = set()

        for category in extracted_menu.categories:
            category_name = category.name.strip()

            for service in category.services:
                service_name = service.name.strip()
                try:
                    variations = await self._resolve_service_variations(service_name, salon_id)
                except Exception as exc:  # noqa: BLE001 - one bad row shouldn't fail the upload
                    logger.warning("Error matching service %r: %s", service_name, exc)
                    continue

                for variation in variations:
                    variation_id = variation.get("salonServiceVariationId", "")
                    if variation_id and variation_id in seen_variation_ids:
                        continue
                    if variation_id:
                        seen_variation_ids.add(variation_id)
                    matched.append(format_variation_response(variation, category_name))

        return matched

    async def _resolve_service_variations(
        self, service_name: str, salon_id: Optional[str]
    ) -> List[dict]:
        """Catalog lookup first, text search as fallback."""
        service_record = await run_in_threadpool(
            self.db_service.find_service_by_name, service_name
        )
        if service_record:
            return await run_in_threadpool(
                self.db_service.find_variations_for_service,
                service_record["serviceId"],
                salon_id,
            )

        logger.debug("No catalog match for %r; falling back to name search", service_name)
        return await run_in_threadpool(
            self.db_service.search_variations_by_name, service_name, salon_id
        )
