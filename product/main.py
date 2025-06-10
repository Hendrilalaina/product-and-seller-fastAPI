from fastapi import FastAPI, HTTPException, status
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from passlib.context import CryptContext

from schema import Product, UpdateProduct, Seller
from database import product_collection, seller_collection

app = FastAPI()
pwd_context = CryptContext(schemes=['sha256_crypt'])

def parse_object_id(id: str):
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{id}' is not a valid ObjectId.",
        )

@app.post('/product',
    response_description="Add new product",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)
async def add_product(product: Product):
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
    seller.password = pwd_context.hash(seller.password)
    new_seller = await seller_collection.insert_one(
        seller.model_dump(by_alias=True, exclude=['id'])
    )
    created_seller = await seller_collection.find_one(
        {'_id': new_seller.inserted_id}
    )
    return created_seller