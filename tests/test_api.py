"""
HTTP-surface tests for /extract-services.

The controller is swapped for a stub via FastAPI's dependency override, so these
tests cover routing, upload validation, and response serialization with no Gemini
call and no database.
"""

import asyncio
import io
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "src"))

os.environ.setdefault("GOOGLE_AI_API_KEY", "test-key")
os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:1")

from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402
from models.service_models import ServiceExtractionResponse  # noqa: E402
from routes.service_routes import get_controller  # noqa: E402


class StubController:
    """Returns a fixed, well-formed response and records what it was called with."""

    def __init__(self):
        self.calls = []

    async def extract_services_from_image(self, image_data, filename, salon_id=None):
        self.calls.append({"size": len(image_data), "filename": filename, "salon_id": salon_id})
        return ServiceExtractionResponse(
            success=True,
            data=[
                {
                    "serviceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                    "name": "Blow Dry",
                    "category": "HAIR",
                    "categoryServiceId": "8b464677-de3d-42dd-b452-d4c224d94196",
                    "duration": 60,
                    "gender": "F",
                    "personType": "A",
                    "price": 1500,
                    "tagNameAndValues": [],
                    "variationId": "6234eb02-0457-40b1-8b5d-fbba0bf98429",
                }
            ],
            metadata={"processed_image": filename, "total_variations_matched": 1},
        )


@pytest.fixture
def client():
    stub = StubController()
    app.dependency_overrides[get_controller] = lambda: stub
    with TestClient(app) as c:
        c.stub = stub
        yield c
    app.dependency_overrides.clear()


def _png_bytes():
    # 1x1 PNG. Content is irrelevant: the Gemini call is stubbed out.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
        "00000049454e44ae426082"
    )


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_extract_returns_matched_variations(client):
    resp = client.post(
        "/api/v1/extract-services",
        files={"file": ("menu.png", _png_bytes(), "image/png")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["variationId"] == "6234eb02-0457-40b1-8b5d-fbba0bf98429"


def test_salon_id_is_passed_through(client):
    client.post(
        "/api/v1/extract-services?salon_id=salon-123",
        files={"file": ("menu.png", _png_bytes(), "image/png")},
    )
    assert client.stub.calls[0]["salon_id"] == "salon-123"


def test_non_image_upload_is_rejected(client):
    resp = client.post(
        "/api/v1/extract-services",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert resp.status_code == 400
    assert "image" in resp.json()["detail"].lower()


def test_empty_upload_is_rejected(client):
    resp = client.post(
        "/api/v1/extract-services",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()
