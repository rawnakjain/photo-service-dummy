"""Shared text-normalization and response-formatting helpers."""

import re
from typing import Any, Dict


def normalize_service_name(name: str) -> str:
    """Collapse a service or variation name to a comparable key.

    Catalog values are snake_case enum names (``basic_cleanup_facial``) while menu
    text is spaced and punctuated (``Basic Cleanup Facial``). Both are reduced to
    lowercase, space-separated words so the two sides match.
    """
    if not name:
        return ""

    normalized = name.lower().strip()
    normalized = normalized.replace("_", " ")
    normalized = re.sub(r"[^\w\s]", "", normalized)  # drop remaining punctuation
    normalized = re.sub(r"\s+", " ", normalized)     # collapse whitespace
    return normalized


def format_variation_response(
    variation_doc: Dict[str, Any], category_name: str = ""
) -> Dict[str, Any]:
    """Project a database variation document onto the API's variation contract.

    ``category_name`` comes from the extracted menu (the salon's own section heading)
    when available, falling back to any category stored on the document.
    """
    return {
        "serviceId": variation_doc.get("serviceId", ""),
        "name": variation_doc.get("salonServiceName", "")
        or variation_doc.get("serviceName", ""),
        "category": category_name or variation_doc.get("category", ""),
        "categoryServiceId": variation_doc.get("serviceId", ""),
        "duration": variation_doc.get("duration", 0),
        "gender": variation_doc.get("forGender", "U"),
        "personType": variation_doc.get("personType", "A"),
        "price": variation_doc.get("price", 0),
        "tagNameAndValues": variation_doc.get("tagNameAndValues", []),
        "variationId": variation_doc.get("salonServiceVariationId", ""),
        # Fields carried through for clients that need more than the core contract.
        "originalPrice": variation_doc.get("originalPrice", 0),
        "bufferInMins": variation_doc.get("bufferInMins", 0),
        "pricingType": variation_doc.get("pricingType", ""),
        "fullName": variation_doc.get("fullName", ""),
        "serviceName": variation_doc.get("serviceName", ""),
        "salonServiceName": variation_doc.get("salonServiceName", ""),
        "salonId": variation_doc.get("salonId", ""),
        "genericService": variation_doc.get("genericService", ""),
        "isCombo": variation_doc.get("isCombo", False),
        "vatCategory": variation_doc.get("vatCategory", ""),
        "pricePerUnit": variation_doc.get("pricePerUnit", 0),
        "unitType": variation_doc.get("unitType", ""),
        "basePriceCalculationType": variation_doc.get("basePriceCalculationType", ""),
    }
