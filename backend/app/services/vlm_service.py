import json
import re
from typing import List,Optional

import torch
from PIL import Image
from transformers import (Qwen3VLForConditionalGeneration,AutoProcessor,)

MODEL_ID ="Qwen/Qwen3-VL-2B-Instruct"

# ============================================================
# LOAD MODEL ONCE
# ============================================================

print("Loading model...")

model = Qwen3VLForConditionalGeneration.from_pretrained(MODEL_ID,
                                                        torch_dtype = torch.float16,
                                                        device_map="auto",)
processor = AutoProcessor.from_pretrained(MODEL_ID)
print("Qwen3-VL model loaded successfully")

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

    messages = [[
        {
            "role":"user",
            "content":[{ 
                "type":"image",
                "image":image,
            },
            {
                "type":"text",
                "text":EXTRACTION_PROMPT,
            },
            ],
        }
    ]]

    text = processor.apply_chat_template(messages[0],tokenize=False,add_generation_prompt=True)
    inputs = processor(
        text=[text],
        images=[image],
        padding=True,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs=  model.generate(**inputs,max_new_tokens=200,)

    input_len = inputs["input_ids"].shape[1]
    generated = outputs[:,input_len:]
    decoded = processor.batch_decode(generated,skip_special_tokens=True,)

    if not decoded:
        return None
    
    return parse_model_output(decoded[0])

# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_leads_batch(images:List[Image.Image],batch_size:int=5,)->List[Optional[dict]]:

    """
    Extract leads from multiple business-card images.

    Images are processed in batches to avoid excessive GPU memory usage.
    """
    results = []
    for i in range(0,len(images),batch_size):
        batch = images[i:i+batch_size]

        messages=[]
        for image in batch:
            messages.append([
                {
                    "role":"user",
                    "content":[{
                        "type":"image",
                        "image":image,
                    },
                    {
                        "type":"text",
                        "text":EXTRACTION_PROMPT,
                    },],
                }
            ]) 

        texts = [ processor.apply_chat_template(message,tokenize=False,add_generation_prompt=True)
                 for message in messages ]
        inputs = processor(
            text=texts,
            images=batch,
            padding=True,
            return_tensors="pt",
            ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(**inputs,max_new_tokens=200,)

            input_len = inputs["input_ids"].shape[1]

            generated = outputs[:,input_len:]
            decoded = processor.batch_decode(generated,skip_special_tokens=True,)

            for text in decoded:
                result = parse_model_output(text)

                results.append(result)
    return results

