import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv(
    "MONGO_URI",
    "mongodb+srv://<username>:<password>@cluster.mongodb.net/?appName=Cluster0"
)
db_name = os.getenv("MONGO_DB_NAME", "zepcruit_practice")

client = MongoClient(mongo_uri)
db = client[db_name]
applications = db["applications"]


# Insert one fake application document
result = applications.insert_one({
    "application_id": "APP001",
    "candidate_name": "Test Candidate",
    "resume_filename": "test_resume.pdf"
})
print("Inserted with id:", result.inserted_id)

# Now fetch it back by application_id
doc = applications.find_one({"application_id": "APP001"})
print("Found:", doc)
