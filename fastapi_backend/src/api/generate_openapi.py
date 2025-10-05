"""
Utility script to generate and write the FastAPI OpenAPI schema.

This script:
- Imports the FastAPI app from src.api.main
- Generates the OpenAPI schema via app.openapi()
- Ensures the description references Google Gemini (not OpenAI)
- Writes the schema to fastapi_backend/interfaces/openapi.json

Run:
  python -m src.api.generate_openapi
"""
import json
import os
import sys
from typing import Any

# Ensure the script runs from the fastapi_backend directory if invoked elsewhere
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
INTERFACES_DIR = os.path.join(BACKEND_ROOT, "interfaces")
OUTPUT_PATH = os.path.join(INTERFACES_DIR, "openapi.json")


def _ensure_gemini_description(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure the OpenAPI 'info.description' mentions Google Gemini.
    This is a non-breaking modification and does not alter endpoints or schemas.
    """
    info = schema.get("info", {})
    desc = info.get("description", "") or ""
    # If description mentions OpenAI, migrate wording to Google Gemini
    if "OpenAI" in desc and "Google Gemini" not in desc:
        desc = desc.replace("OpenAI", "Google Gemini")
    # If no mention, but we want to be explicit, append a clarifier.
    if "Google Gemini" not in desc:
        if desc:
            desc = f"{desc.rstrip()} Using Google Gemini for answer generation."
        else:
            desc = "Backend API for an AI Copilot that answers user questions using Google Gemini."
    info["description"] = desc
    schema["info"] = info
    return schema


def main() -> int:
    # Import the FastAPI app
    try:
        from src.api.main import app
    except Exception as e:
        print(f"Failed to import FastAPI app: {e}", file=sys.stderr)
        return 1

    # Generate schema
    try:
        openapi_schema = app.openapi()
    except Exception as e:
        print(f"Failed to generate OpenAPI schema: {e}", file=sys.stderr)
        return 1

    # Patch description to ensure Google Gemini is referenced
    try:
        openapi_schema = _ensure_gemini_description(openapi_schema)
    except Exception as e:
        print(f"Failed to adjust schema description: {e}", file=sys.stderr)
        return 1

    # Ensure interfaces dir exists
    os.makedirs(INTERFACES_DIR, exist_ok=True)

    # Write schema
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        print(f"Wrote OpenAPI schema to {OUTPUT_PATH}")
        return 0
    except Exception as e:
        print(f"Failed to write OpenAPI schema: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
