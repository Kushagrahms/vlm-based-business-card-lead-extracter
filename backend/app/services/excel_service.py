import pandas as pd

def leads_to_excel(leads):
    rows=[]

    for lead in leads:
        if hasattr(lead,"model_dump"):
            data = lead.model_dump()
        elif hasattr(lead,"dict"):
            data = lead.dict()
        else:
            data = lead

        rows.append({
            "First Name":data.get("first_name",""),
            "Last Name":data.get("last_name",""),
            "Position/Job title":data.get("job_title",""),
            "Company":data.get("company",""),
            "Location":data.get("location",""),
            "Phone Number":data.get("phone_number",""),
            "Email Address":data.get("email",""),

        })
    return pd.DataFrame(rows)
