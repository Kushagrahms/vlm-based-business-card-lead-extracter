import json
import re
import os
from typing import List,Optional

from PIL import Image
from gradio_client import Client, handle_file

# ============================================================
# Online model connection
# ============================================================
QWEN_SPACE = os.getenv(
    "QWEN_SPACE","YOUR_HUGGINGFACE_USERNAME/YOUR_SPACE_NAME"
)


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
Extract all business card information visible in the image.

Return ONLY a valid JSON object with exactly these fields:

{
  "first_name": "",
  "last_name": "",
  "job_title": "",
  "company": "",
  "location": "",
  "phone": "",
  "email": ""
}

IMPORTANT ACCURACY RULES:

1. NAME:
- Identify the person's actual name.
- Do not use the company name as the person's name.

2. JOB TITLE:
- Extract the person's actual position/job title.
- Do not use the company name as the job title.

3. COMPANY:
- Extract the actual organization/company name.

4. LOCATION:
- Carefully read the address EXACTLY as visible.
- Preserve street numbers, street names, city, state, ZIP/postal code.
- Do NOT guess, correct, or invent an address.
- Do NOT replace unclear characters with a guessed value.
- Copy what is actually visible.

5. PHONE:
- Carefully read EVERY digit.
- Preserve the phone number exactly as visible.
- Do NOT invent or correct digits.
- If multiple phone numbers exist, separate them with ", ".
- If the same number appears more than once, include it only once.

6. EMAIL:
- Extract only actual email addresses containing @.
- Do not put website URLs in email.

7. MISSING INFORMATION:
- Use "" if the information is not visible.

Return ONLY the JSON object.
"""


# ============================================================
# JSON CLEANING
# ============================================================

def parse_model_output(text:str)->Optional[dict]:
    """
    Convert Qwen's generated text into a Python dictionary.
    """
    try:
        text = text.strip()
         # Removing markdown JSON fences if the model adds them
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)

        return json.loads(text)
    except (json.DecodeError, TypeError):
        return None
# ============================================================
# SINGLE IMAGE EXTRACTION
# ============================================================

def extract_lead(image:Image.Image)->Optional[dict]:
    """
    Extract structured lead information from one business-card image.
    """

    client = Client(QWEN_SPACE)
    result = client.predict(
        image= handle_file(image),
        prompt = EXTRACTION_PROMPT,
        api_name = "/predict",
    )

    if  isinstance(result,tuple):
        result = result[0]
    if isinstance(result,dict):
        return result 
    if isinstance(result,str):
        return parse_model_output(result) 

    return None

# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_leads_batch(images:List[Image.Image],batch_size:int=5,)->List[Optional[dict]]:

    """
    Extract leads from multiple business-card images.

    Images are processed in batches to avoid excessive GPU memory usage.
    """
    results = []
    for image in images:
        try:
            result.extract_lead(image)
        except Exception as e:
            print(f"Qwen extraction failed: {e}")
            result = None

        results.append(result)

    return results   