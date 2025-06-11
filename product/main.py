from fastapi import FastAPI, HTTPException, status
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from schema import Product, UpdateProduct, Seller, User, Token
from database import product_collection, seller_collection

app = FastAPI()
pwd_context = CryptContext(schemes=['sha256_crypt'])

SECRET_KEY = "eb45fc2d7e0c48a80db403d5156856b71a1b1d44009f603738f5ed495093add5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 20

def parse_object_id(id: str):
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{id}' is not a valid ObjectId.",
        )

def generate_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

async def email_unique(email: str):
    if await seller_collection.find_one({'email': email}):
        raise HTTPException(status_code=400, detail="Email already in use")

async def check_seller(id: str):
    if await seller_collection.find_one({'_id': parse_object_id(id)}) is None:    
        raise HTTPException(status_code=404, detail="Seller is not found")

@app.post('/product',
    response_description="Add new product",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)
async def add_product(product: Product):
    await check_seller(product.seller_id)
    new_product = await product_collection.insert_one(
        product.model_dump(by_alias=True, exclude=['id'])
    )
    created_product = await product_collection.find_one(
        {'_id': new_product.inserted_id}
    )
    return created_product

@app.get('/product',
    response_description="Get all products",
    response_model=List[Product],
    response_model_by_alias=False
)
async def get_products():
    return await product_collection.find().to_list()

@app.get('/product/{id}',
    response_description="Get a product by id",
    response_model=Product,
    response_model_by_alias=False
)
async def get_product(id: str):
    if (
        product := await product_collection.find_one({'_id': parse_object_id(id)})
    ) is not None:
        return product
    
    raise HTTPException(status_code=404, detail=f"Product {id} not found")

@app.put('/product/{id}',
    response_description="Update a product",
    response_model=Product,
    response_model_by_alias=False    
)
async def update_product(id: str, product: UpdateProduct):
    product = {
        k: v for k, v in product.model_dump(by_alias=True).items() if v is not None
    }

    if 'seller_id' in product.keys():
        await check_seller(product['seller_id'])
    if len(product) >= 1:
        update_product = await product_collection.find_one_and_update(
            {"_id": parse_object_id(id)},
            {"$set": product},
            return_document=ReturnDocument.AFTER
        )
        if update_product is not None:
            return update_product
        else:
            raise HTTPException(status_code=404, detail=f"Product {id} is not found")

    # len(product) == 0 but id exists
    if (exist_product := await product_collection.find_one({'_id': parse_object_id(id)})) is not None:
        return exist_product
    
    raise HTTPException(status_code=404, detail=f"Product {id} is not found")

@app.post('/seller',
    response_description="Add a seller",
    response_model=Seller,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED
)
async def add_seller(seller: Seller):
    await email_unique(seller.email)
    seller.password = pwd_context.hash(seller.password)
    new_seller = await seller_collection.insert_one(
        seller.model_dump(by_alias=True, exclude=['id'])
    )
    created_seller = await seller_collection.find_one(
        {'_id': new_seller.inserted_id}
    )
    return created_seller

@app.post('/login',
    response_description="Login the seller",
    response_model=Token,
    response_model_by_alias=False
)
async def login_seller(user: User):
    seller = await seller_collection.find_one(
        {'email': user.email}
    )
    if not seller:
        raise HTTPException(status_code=404, detail=f"User email {user.email} is not found")
    
    if not pwd_context.verify(secret=user.password, hash=seller['password']):
        raise HTTPException(status_code=404, detail=f"Invalid password")
    
    access_token = generate_token(
        data={'sub': seller['username']}
    )
    token = Token(access_token = access_token,token_type = 'bearer')
    return token