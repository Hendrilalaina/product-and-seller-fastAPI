import motor.motor_asyncio
from fastapi import FastAPI, Body, status
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from bson import ObjectId

app = FastAPI()

MONGODB_URL="mongodb://127.0.0.1?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.fastapi
product_collection = db.get_collection('product')

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str 
    price: int
    discount: int
    discount_price: float
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

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
    response_model=List[Product],
    response_model_by_alias=False
)
async def get_products():
    products = await product_collection.find().to_list()
    return products