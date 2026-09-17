from pydantic import BaseModel

class Lead(BaseModel):
    first_name: str = ""
    last_name: str = ""
    job_title: str = ""
    company: str = ""
    location: str = ""
    phone_number: str = ""
    email: str = ""
    
    