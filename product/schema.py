from pydantic import BaseModel, Field, ConfigDict, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Optional
from typing_extensions import Annotated
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]


class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str 
    price: int
    discount: int
    discount_price: float
    seller_id: PyObjectId = Field(default=None)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UpdateProduct(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    discount: Optional[int] = None
    discount_price: Optional[float] = None
    seller_id: Optional[PyObjectId] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Seller(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    username: str
    email: EmailStr
    password: str
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class User(BaseModel):
    email: EmailStr = None
    password: str = None