from io import BytesIO
from fastapi.responses import StreamingResponse
from app.services.excel_service import leads_to_excel
from typing import Annotated
from fastapi import APIRouter,UploadFile,File, HTTPException
from PIL import Image
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.lead import Lead
from app.services.vlm_service import extract_leads_batch

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads"],
)
@router.post("/extract")
async def extract_leads(files:Annotated[list[UploadFile], File(...)]):
    """
    Upload multiple business-card images
    and extract structured lead information using Qwen3-VL.
    """

    if not files :
        raise HTTPException(status_code=400,detail="No images uploaded")

    images=[]

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400,detail=f"{file.filename} is not a valid image")

        try:
            contents = await file.read()
            image = Image.open(__import__("io").BytesIO(contents)).convert("RGB")
            images.append(image)

        except Exception:
            raise HTTPException(status_code=400,detail=f"Could not read image:{file.filename}")

    try:
        results = extract_leads_batch(images,batch_size=5)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"VLM extraction failed: {str(e)}")

    # -----------------------------
    # SAVE TO DATABASE
    # -----------------------------
    db : Session = SessionLocal()

    leads=[]
    try:
        for index, result in enumerate(results):
            lead = Lead(
                first_name=result.get("first_name",""),
                last_name=result.get("last_name",""),
                job_title=result.get("job_title",""),
                company=result.get("company",""),
                location=result.get("location",""),
                phone_number=result.get("phone_number", result.get("phone", "")),
                email=result.get("email",""),
                source_filename=files[index].filename,
            )
            db.add(lead)
            leads.append({
                    "filename": files[index].filename,
                    "data": {
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "job_title": lead.job_title,
                    "company": lead.company,
                    "location": lead.location,
                    "phone_number": lead.phone_number,
                    "email": lead.email,
                }
            })
        db.commit()
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database save failed: {str(e)}"
        )

    finally:
        db.close()

    return {
        "count":len(leads),
        "leads":leads,    }

@router.get("")
def get_leads():
    db:Session = SessionLocal()

    try:
        leads = db.query(Lead).order_by(Lead.id.desc()).all()

        return {
            "count": len(leads),
            "leads": [
                {
                    "id": lead.id,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "job_title": lead.job_title,
                    "company": lead.company,
                    "location": lead.location,
                    "phone_number": lead.phone_number,
                    "email": lead.email,
                    "source_filename": lead.source_filename,
                }
                for lead in leads
            ],
        }

    finally:
        db.close()

@router.get("/export")
def export_leads():
    """
    Export all saved leads as an Excel file.
    """

    db: Session = SessionLocal()

    try:
        leads = db.query(Lead).order_by(Lead.id.desc()).all()

        data = [
            {
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "job_title": lead.job_title,
                "company": lead.company,
                "location": lead.location,
                "phone_number": lead.phone_number,
                "email": lead.email,
            }
            for lead in leads
        ]

        dataframe = leads_to_excel(data)

        output = BytesIO()

        dataframe.to_excel(
            output,
            index=False,
            engine="openpyxl"
        )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="business_card_leads.xlsx"'
                )
            },
        )

    finally:
        db.close()