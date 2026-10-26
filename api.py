import os
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI, UploadFile
from modules.parser import extract_text

load_dotenv()

app = FastAPI()


@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile):
    text = extract_text(file.file, filename=file.filename)
    return {"extracted_text": text}


# Reuse connection pattern via environment variables
mongo_uri = os.getenv(
    "MONGO_URI",
    "mongodb+srv://<username>:<password>@cluster.mongodb.net/?appName=Cluster0"
)
db_name = os.getenv("MONGO_DB_NAME", "zepcruit_practice")

mongo_client = MongoClient(mongo_uri)
db = mongo_client[db_name]
applications = db["applications"]



@app.get("/application/{application_id}")
async def get_application(application_id: str):
    doc = applications.find_one({"application_id": application_id})
    if doc is None:
        return {"error": "Application not found"}
    doc["_id"] = str(doc["_id"])  # ObjectId isn't JSON-serializable by default
    return doc
