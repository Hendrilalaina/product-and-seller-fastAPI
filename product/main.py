from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pymongo import ReturnDocument
from util import email_unique, parse_object_id
from auth import generate_token, get_current_user, hash_password, verify_password
from schema import Product, UpdateProduct, Seller, Token, UserRequest
from database import product_collection, seller_collection

app = FastAPI(
    title="Products API",
    description="Manage products in website",
    contact={
        "email": "hendrilalaina@gmail.com",
    },)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"],)

@app.post('/seller',
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

@app.post('/login',
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

@app.get('/me',
    tags=["Authentication"],
    description="The login user",
    response_model=Seller,
    response_model_exclude={"password"},)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get('/product',
    tags=["Product"],
    description="Get all products",
    response_model=List[Product],
    response_model_by_alias=False,)
async def get_products():
    return await product_collection.find().to_list()

@app.get('/product/{id}',
    tags=["Product"],
    description="Get a product by id",
    response_model=Product,
    response_model_by_alias=False,)
async def get_product(id: str):
    if (
        product := await product_collection.find_one({'_id': parse_object_id(id)})
    ) is not None:
        return product
    
    raise HTTPException(status_code=404, detail=f"Product {id} not found")

@app.post('/product',
    tags=["Product"],
    description="Add new product",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)
async def add_product(product: Product, seller: dict = Depends(get_current_user)):
    product.seller_id = str(seller['_id'])
    new_product = await product_collection.insert_one(
        product.model_dump(by_alias=True, exclude=['id']))

    created_product = await product_collection.find_one(
        {'_id': new_product.inserted_id})

    return created_product

@app.put('/product/{id}',
    tags=["Product"],
    description="Update a product",
    response_model=Product,
    response_model_by_alias=False,)
async def update_product(id: str, product: UpdateProduct, seller: dict = Depends(get_current_user)):
    product = {
        k: v for k, v in product.model_dump(by_alias=True).items() if v is not None
    }
    
    if len(product) >= 1:
        update_product = await product_collection.find_one_and_update(
            {"_id": parse_object_id(id), "seller_id": seller['_id']},
            {"$set": product},
            return_document=ReturnDocument.AFTER,)

        if update_product is not None:
            return update_product
        else:
            raise HTTPException(status_code=404, detail=f"Product {id} is not found")

    # len(product) == 0 but id exists
    if (exist_product := await product_collection.find_one({'_id': parse_object_id(id)})) is not None:
        return exist_product
    
    raise HTTPException(status_code=404, detail=f"Product {id} is not found")

@app.delete('/product/{id}',
    tags=["Product"],
    description="Remove a product",)
async def delete_product(id: str, seller: dict = Depends(get_current_user)):
    remove_product = await product_collection.find_one_and_delete(
        {"_id": parse_object_id(id), "seller_id": seller['_id']}
    )
    if not remove_product:
        raise HTTPException(status_code=404, detail=f"Product {id} is not found!")
    return f"Product {id} is deleted!"
