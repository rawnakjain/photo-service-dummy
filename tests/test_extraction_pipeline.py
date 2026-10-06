"""
Tests for the extraction-to-matching pipeline.

The Gemini call itself is stubbed: it depends on a live API key and a network,
neither of which a unit test should require. Everything downstream of the model
response is real — normalization, database matching, and response formatting.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "src"))

os.environ.setdefault("GOOGLE_AI_API_KEY", "test-key")
os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:1")  # forces mock mode

from controllers.service_extraction_controller import ServiceExtractionController  # noqa: E402
from services.database_service import DatabaseService  # noqa: E402
from services.gemini_service import Category, Menu, PriceVariant, Service  # noqa: E402
from utils.normalizers import normalize_service_name  # noqa: E402


@pytest.fixture
def controller():
    # Built with __new__ so the Gemini client (and its API-key requirement) is never
    # touched: these tests exercise only the matching and formatting stages.
    ctrl = ServiceExtractionController.__new__(ServiceExtractionController)
    ctrl._gemini_service = None
    ctrl.db_service = DatabaseService()
    assert ctrl.db_service.use_mock, "test requires mock mode (no live MongoDB)"
    return ctrl


def make_menu():
    """A menu shaped like what Gemini returns for a typical price list."""
    return Menu(
        salon_name="Test Salon",
        currency="INR",
        categories=[
            Category(
                name="HAIR",
                services=[
                    Service(
                        name="Blow Dry",
                        variants=[PriceVariant(raw="1500/-", amount=1500)],
                        duration_minutes=60,
                    ),
                ],
            ),
            Category(
                name="FACIAL",
                services=[
                    Service(
                        name="Basic Cleanup Facial",
                        variants=[PriceVariant(raw="1000/-", amount=1000)],
                        duration_minutes=45,
                    ),
                ],
            ),
        ],
    )


def test_exact_name_match_returns_variations(controller):
    """A service name that matches the catalog should pull its variations through."""
    menu = make_menu()
    result = asyncio.run(
        controller._match_services_with_database(menu, salon_id=None)
    )
    assert len(result) == 2, f"expected two matched variations, got {len(result)}"

    names = {v["name"] for v in result}
    assert "Clean Up" in names, "Basic Cleanup Facial should match 'Clean Up' variation"
    assert "Blow Dry" in names


def test_response_shape_matches_required_schema(controller):
    """Every mapped object must carry the fields the client reads."""
    menu = make_menu()
    result = asyncio.run(
        controller._match_services_with_database(menu, salon_id=None)
    )
    required = {
        "serviceId", "name", "category", "categoryServiceId",
        "duration", "gender", "personType", "price",
        "tagNameAndValues", "variationId",
    }
    for variation in result:
        missing = required - set(variation)
        assert not missing, f"variation missing fields {missing}: {variation}"


def test_category_is_carried_from_menu(controller):
    """The menu's own section heading should survive into the response."""
    menu = make_menu()
    result = asyncio.run(
        controller._match_services_with_database(menu, salon_id=None)
    )
    categories = {v["category"] for v in result}
    assert "FACIAL" in categories or "HAIR" in categories


def test_salon_filter_excludes_other_salons(controller):
    """Passing a salon_id that owns nothing should yield no matches."""
    menu = make_menu()
    result = asyncio.run(
        controller._match_services_with_database(menu, salon_id="nonexistent-salon")
    )
    assert result == [], f"expected no matches for foreign salon, got {result}"


def test_unmatched_service_falls_through_to_text_search(controller):
    """A name absent from the catalog exercises the variation-name fallback."""
    menu = Menu(
        currency="INR",
        categories=[
            Category(
                name="MASSAGE",
                services=[
                    Service(
                        name="Head Massage",
                        variants=[PriceVariant(raw="400/-", amount=400)],
                    ),
                ],
            ),
        ],
    )
    result = asyncio.run(
        controller._match_services_with_database(menu, salon_id=None)
    )
    assert len(result) >= 1, "text-search fallback should still find 'Head Massage'"
    assert any(v["fullName"] == "Head Massage" for v in result)


def test_database_service_normalizes_names():
    assert normalize_service_name("Blow Dry!") == "blow dry"
    assert normalize_service_name("  Hair   Cut  ") == "hair cut"
    assert normalize_service_name("basic_cleanup_facial") == "basic cleanup facial"
    assert normalize_service_name("") == ""
