from fastapi import FastAPI, status
from typing import List

from schema import Product
from database import product_collection

app = FastAPI()

@app.post('/product',
    response_description="Add new product",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,)
async def add_product(product: Product):
    print("Call API '/product'")
    new_product = await product_collection.insert_one(
        product.model_dump(by_alias=True, exclude=['id'])
    )
    created_product = await product_collection.find_one(
        {'_id': new_product.inserted_id}
    )
    return created_product

@app.get('/products',
    response_description="Get all products",
    response_model=List[Product],
    response_model_by_alias=False
)
async def get_products():
    products = await product_collection.find().to_list()
    return products