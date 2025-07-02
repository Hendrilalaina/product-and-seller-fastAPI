from fastapi import APIRouter, status, HTTPException, Depends

from product.service import hash_password, verify_password, get_current_user, generate_token
from product.schema import Seller
from product.util import email_unique
from product.database import seller_collection
from product.schema import Token, UserRequest

router = APIRouter()

@router.post('/seller',
    tags=["Authentication"],
    description="Register a seller",
    response_model=Seller,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,)
async def add_seller(seller: Seller):
    await email_unique(seller.email)

    seller.password = hash_password(seller.password)
    new_seller = await seller_collection.insert_one(
        seller.model_dump(by_alias=True, exclude=['id']))

    created_seller = await seller_collection.find_one(
        {'_id': new_seller.inserted_id})

    return created_seller

@router.post('/login',
    tags=["Authentication"],
    description="Login the seller",
    response_model=Token,
    response_model_by_alias=False,)
async def login_seller(user_request: UserRequest):
    seller = await seller_collection.find_one({'email': user_request.email})
    if not seller:
        raise HTTPException(status_code=404, detail="User email not found")
    
    if not verify_password(user_request.password, seller['password']):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = generate_token(
        data={"sub": seller["username"]})

    return Token(access_token=access_token, token_type="bearer")

@router.get('/me',
    tags=["Authentication"],
    description="The login user",
    response_model=Seller,
    response_model_exclude={"password"},)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user
