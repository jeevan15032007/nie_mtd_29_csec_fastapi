from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pymongo import MongoClient
from bson import ObjectId

# app
app = FastAPI()

# db configuration
URL = "mongodb://127.0.0.1:27017"
client = MongoClient(URL)

hospital_db = client["hospital_support_db"]
hospital_request_collection = hospital_db["hospital_requests"]


# schema pydantic
class HospitalRequestCreate(BaseModel):
    patient_department: str
    issue_title: str
    issue_description: str
    request_category: str
    request_status: str
    assigned_staff: str = ""


class HospitalRequestResponse(HospitalRequestCreate):
    request_id: str


# helper
def hospital_request_helper(hospital_request_doc):
    return {
        "request_id": str(hospital_request_doc["_id"]),
        "patient_department": hospital_request_doc["patient_department"],
        "issue_title": hospital_request_doc["issue_title"],
        "issue_description": hospital_request_doc["issue_description"],
        "request_category": hospital_request_doc["request_category"],
        "request_status": hospital_request_doc["request_status"],
        "assigned_staff": hospital_request_doc.get("assigned_staff", "")
    }


# APIs - CRUD
# create, read all, read by id, update, delete


# CREATE HOSPITAL REQUEST
@app.post(
    "/hospital-requests",
    status_code=201,
    response_model=HospitalRequestResponse
)
def hospital_request_create(payload: HospitalRequestCreate):

    hospital_request_dict = payload.model_dump()

    result = hospital_request_collection.insert_one(
        hospital_request_dict
    )

    new_hospital_request = hospital_request_collection.find_one(
        {"_id": result.inserted_id}
    )

    return hospital_request_helper(new_hospital_request)


# READ ALL HOSPITAL REQUESTS
@app.get(
    "/hospital-requests",
    response_model=list[HospitalRequestResponse]
)
def hospital_request_read_all():

    hospital_request_docs = hospital_request_collection.find()

    hospital_requests = [
        hospital_request_helper(doc)
        for doc in hospital_request_docs
    ]

    return hospital_requests


# READ HOSPITAL REQUEST BY ID
@app.get(
    "/hospital-requests/{request_id}",
    response_model=HospitalRequestResponse
)
def hospital_request_read_by_id(request_id: str):

    if not ObjectId.is_valid(request_id):
        raise HTTPException(
            detail="Invalid Hospital Request ID",
            status_code=400
        )

    hospital_request_doc = hospital_request_collection.find_one(
        {"_id": ObjectId(request_id)}
    )

    if not hospital_request_doc:
        raise HTTPException(
            detail="Hospital Request Not Found",
            status_code=404
        )

    return hospital_request_helper(hospital_request_doc)


# UPDATE HOSPITAL REQUEST
@app.put(
    "/hospital-requests/{request_id}",
    response_model=HospitalRequestResponse
)
def hospital_request_update(
    request_id: str,
    payload: HospitalRequestCreate
):

    if not ObjectId.is_valid(request_id):
        raise HTTPException(
            detail="Invalid Hospital Request ID",
            status_code=400
        )

    hospital_request_dict = payload.model_dump()

    result = hospital_request_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": hospital_request_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(
            detail="Hospital Request Not Found",
            status_code=404
        )

    updated_hospital_request = hospital_request_collection.find_one(
        {"_id": ObjectId(request_id)}
    )

    return hospital_request_helper(updated_hospital_request)


# DELETE HOSPITAL REQUEST
@app.delete("/hospital-requests/{request_id}")
def hospital_request_delete(request_id: str):

    if not ObjectId.is_valid(request_id):
        raise HTTPException(
            detail="Invalid Hospital Request ID",
            status_code=400
        )

    result = hospital_request_collection.delete_one(
        {"_id": ObjectId(request_id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            detail="Hospital Request Not Found",
            status_code=404
        )

    return {
        "message": "Hospital Request Deleted Successfully"
    }
