from sqlalchemy import Column,Integer,String, Text
from app.database.database import Base

class Lead(Base):
    __tablename__ = "Leads"
    id = Column(Integer,primary_key=True,index=True)

    first_name = Column(String(70),default="")
    last_name = Column(String(70),default="")
    job_title = Column(String(70),default="")
    company = Column(String(70),default="")
    location = Column(String(150),default="")
    phone_number = Column(String(70),default="")
    email = Column(String(70),default="")

    source_filename = Column(String(200),default="")