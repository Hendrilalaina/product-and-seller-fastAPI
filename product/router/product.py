from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from pymongo import ReturnDocument

from product.service import get_current_user
from product.schema import Product, UpdateProduct
from product.database import product_collection
from product.util import parse_object_id

router = APIRouter()

@router.get('/product',
    tags=["Product"],
    description="Get all products",
    response_model=List[Product],
    response_model_by_alias=False,)
async def get_products():
    return await product_collection.find().to_list()

@router.get('/product/{id}',
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

@router.post('/product',
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

@router.put('/product/{id}',
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

@router.delete('/product/{id}',
    tags=["Product"],
    description="Remove a product",)
async def delete_product(id: str, seller: dict = Depends(get_current_user)):
    remove_product = await product_collection.find_one_and_delete(
        {"_id": parse_object_id(id), "seller_id": seller['_id']}
    )
    if not remove_product:
        raise HTTPException(status_code=404, detail=f"Product {id} is not found!")
    return f"Product {id} is deleted!"
