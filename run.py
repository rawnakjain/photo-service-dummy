#!/usr/bin/env python3
"""
Launcher for the Salon Services Extraction API.

Sets up the module search path (including an optional external site-packages
directory for the Google GenAI SDK) and starts the FastAPI server.
"""

import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))

# Load .env before reading GENIAI_PACKAGE_PATH, so the launcher and the app agree.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(HERE) / ".env")
except ImportError:  # dotenv not installed yet; env vars still work
    pass

# Optional: point at an existing environment that already ships google-genai.
# This must go in *before* any other site-packages so the `google` namespace
# resolves to the copy that actually contains `genai`.
genai_path = os.getenv("GENIAI_PACKAGE_PATH")
if genai_path and os.path.isdir(genai_path) and genai_path not in sys.path:
    sys.path.insert(0, genai_path)

# Make `src` importable as a package root and add the project's own directory.
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import uvicorn  # noqa: E402

if __name__ == "__main__":
    from app import app  # noqa: E402

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)