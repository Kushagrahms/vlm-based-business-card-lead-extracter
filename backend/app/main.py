from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi 
from app.routes.leads import router as leads_router
from app.database.database import Base, engine
from app.models.lead import Lead
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title = "Business card lead extraction API",
    version = "1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#API Routes:
app.include_router(leads_router) 

@app.get("/")
def root():
    return {
        "message" : "Business card lead extraction API",
        "status" : "Running"
    }
@app.get("/health")
def health():
    return {"status" : "healthy"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title = app.title,
        version = app.version,
        routes = app.routes,
    )

#fix for swagger UI rendering issue for uplaoding files:
    schemas = schema.get("components", {}).get("schemas", {})

    for schema_name, schema_definition in schemas.items():

        properties = schema_definition.get("properties", {})

        for field_name, field_definition in properties.items():

            # Multiple file uploads
            if field_definition.get("type") == "array":

                items = field_definition.get("items", {})

                if items.get("contentMediaType") == "application/octet-stream":
                    items.pop("contentMediaType", None)
                    items["format"] = "binary"

            # Single file upload
            elif field_definition.get("type") == "string":

                if field_definition.get("contentMediaType") == "application/octet-stream":
                    field_definition.pop("contentMediaType", None)
                    field_definition["format"] = "binary"

    app.openapi_schema = schema

    return app.openapi_schema


app.openapi = custom_openapi



