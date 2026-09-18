import os
from io import BytesIO
from typing import List, Optional

import requests
from PIL import Image
from dotenv import load_dotenv


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()

KAGGLE_VLM_URL = os.getenv("KAGGLE_VLM_URL")

if not KAGGLE_VLM_URL:
    raise RuntimeError(
        "KAGGLE_VLM_URL environment variable is not set."
    )


# ============================================================
# Normalize Kaggle response
# ============================================================

def normalize_result(data: dict) -> dict:
    return {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "job_title": data.get(
            "position",
            data.get("job_title", "")
        ),
        "company": data.get("company", ""),
        "location": data.get("location", ""),
        "phone_number": data.get(
            "phone_number",
            data.get("phone", "")
        ),
        "email": data.get(
            "email_address",
            data.get("email", "")
        ),
    }


# ============================================================
# Extract one business card
# ============================================================

def extract_lead(image: Image.Image) -> Optional[dict]:

    try:

        # ----------------------------------------------------
        # Convert PIL image to JPEG bytes
        # ----------------------------------------------------

        buffer = BytesIO()

        image.convert("RGB").save(
            buffer,
            format="JPEG",
            quality=95
        )

        image_bytes = buffer.getvalue()

        # ----------------------------------------------------
        # Prepare multipart upload
        # ----------------------------------------------------

        files = {
            "file": (
                "business_card.jpg",
                image_bytes,
                "image/jpeg"
            )
        }

        # ----------------------------------------------------
        # Send image to Kaggle
        # ----------------------------------------------------

        print(f"Sending image to Kaggle: {KAGGLE_VLM_URL}")

        response = requests.post(
            KAGGLE_VLM_URL,
            files=files,
            timeout=180
        )

        print(f"Kaggle response status: {response.status_code}")

        response.raise_for_status()

        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        result = response.json()

        print("Kaggle response:", result)

        if not result.get("success", False):
            raise RuntimeError(
                result.get(
                    "error",
                    "Kaggle VLM extraction failed"
                )
            )

        data = result.get("data")

        if not isinstance(data, dict):
            raise ValueError(
                "Invalid data returned from Kaggle VLM API"
            )

        # ----------------------------------------------------
        # Normalize field names
        # ----------------------------------------------------

        return normalize_result(data)

    except requests.exceptions.Timeout:
        print("Kaggle VLM request timed out")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Kaggle VLM request failed: {e}")
        return None

    except Exception as e:
        print(f"VLM extraction error: {e}")
        return None


# ============================================================
# Extract multiple business cards
# ============================================================

def extract_leads_batch(
    images: List[Image.Image],
    batch_size: int = 5
) -> List[Optional[dict]]:

    results = []

    for image in images:

        result = extract_lead(image)

        results.append(result)

    return results