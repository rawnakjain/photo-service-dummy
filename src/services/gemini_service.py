"""Gemini Flash wrapper for salon-menu extraction.

The Google GenAI SDK is imported lazily rather than at module import time. That
keeps this module (and everything importing it) usable in environments where the
SDK is not installed — tests, packaging, health checks — with the dependency
only materialising when an extraction is actually attempted.
"""

import os
import sys
import logging
import json
from typing import List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# Pydantic models mirroring the shape the model must return. These are handed to
# Gemini as response_schema, so they are the contract, not merely validation.
class PriceVariant(BaseModel):
    label: Optional[str] = None
    amount: Optional[float] = None
    is_starting_price: bool = False
    raw: Optional[str] = None


class Service(BaseModel):
    name: str
    variants: List[PriceVariant]
    duration_minutes: Optional[int] = None


class Category(BaseModel):
    name: str
    services: List[Service]


class Menu(BaseModel):
    salon_name: Optional[str] = None
    tagline: Optional[str] = None
    currency: str = "INR"
    categories: List[Category]
    warnings: List[str] = []


def _add_genai_path() -> None:
    """Make an externally-supplied GenAI install importable.

    Some deployments run this service against an interpreter that already has
    ``google-genai`` installed elsewhere (for example a sibling project's virtualenv).
    ``GENIAI_PACKAGE_PATH`` points at that site-packages directory. It is prepended,
    never appended, so the copy containing ``genai`` wins the namespace lookup.
    """
    path = os.getenv("GENIAI_PACKAGE_PATH")
    if path and os.path.isdir(path) and path not in sys.path:
        sys.path.insert(0, path)
        logger.info("Added %s to sys.path for google-genai", path)


class GeminiService:
    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None

        api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_AI_API_KEY environment variable is not set; "
                "get a key at https://aistudio.google.com/apikey"
            )
        self.api_key = api_key

    @property
    def client(self):
        """Build the GenAI client on first use."""
        if self._client is None:
            _add_genai_path()
            from google import genai  # imported here so the module loads without the SDK
            from google.genai import types  # noqa: F401  (validated below)

            self._genai = genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _types(self):
        from google.genai import types

        return types

    def _parse_response(self, response) -> Menu:
        """Read a Menu out of a Gemini response, tolerating prose-wrapped JSON."""
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, Menu):
            return parsed
        if isinstance(parsed, dict):
            return Menu.model_validate(parsed)

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise ValueError("Gemini returned neither parsed output nor text")

        try:
            return Menu.model_validate(json.loads(text))
        except json.JSONDecodeError:
            pass

        # The model sometimes wraps the object in prose despite the schema; recover it.
        start, depth, in_string, escaped = text.find("{"), 0, False, False
        if start == -1:
            raise ValueError(f"no JSON object found in Gemini response: {text[:200]!r}")
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    payload = json.loads(text[start : index + 1])
                    return Menu.model_validate(payload)
        raise ValueError("unbalanced JSON object in Gemini response")

    async def extract_menu_from_image(self, image_data: bytes, prompt: str) -> Menu:
        """Extract a structured :class:`Menu` from raw image bytes."""
        types = self._types()
        image_part = types.Part.from_bytes(data=image_data, mime_type="image/jpeg")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Menu,
                temperature=0.0,
            ),
        )
        return self._parse_response(response)
