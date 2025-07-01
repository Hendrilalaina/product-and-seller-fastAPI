from fastapi import HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

from database import seller_collection

def parse_object_id(id: str):
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{id}' is not a valid ObjectId.",
        )

async def email_unique(email: str):
    if await seller_collection.find_one({'email': email}):
        raise HTTPException(status_code=400, detail="Email already in use")

async def check_seller(id: str):
    if await seller_collection.find_one({'_id': parse_object_id(id)}) is None:    
        raise HTTPException(status_code=404, detail="Seller is not found")

async def get_seller_by_username(username: str):
    return await seller_collection.find_one({"username": username})