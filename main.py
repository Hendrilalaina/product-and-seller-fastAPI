from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl
from typing import Set, List

class Profile(BaseModel):
    name: str
    email: str
    age: int

class Image(BaseModel):
    url: HttpUrl
    name: str

class Product(BaseModel):
    name: str = Field(examples=["Laptop"])
    price: int = Field(title="Price of the product",
                        description="Must greater than 0",
                        gt=0)
    discount: int
    discount_price: float
    tags: Set[str] = Field(examples=[["it", "electronics"]])
    images: List[Image]


class Offer(BaseModel):
    name: str
    description: str
    price: int
    products: List[Product]

class User(BaseModel):
    name: str
    email: str

app = FastAPI()

@app.get('/')
def home():
    return "Hello world"

@app.get('/user/admin')
def admin():
    return {"Your are in the admin route"}

@app.get('/user/{username}')
def profile(username: str):
    return {f"This is a profile page for {username}"}

@app.get('/movies/{id}')
def movie(id):
    return {f"This is the movie of {id}"}

@app.get('/movies')
def movies():
    return {'movie list': ['Movie 1', 'Movie 2']}

@app.post('/user')
def add_profile(profile: Profile):
    return profile

@app.post('/product/{product_id}')
def add_product(product: Product, product_id: int, category: str):
    product.discount_price = product.price \
        - (product.price * product.discount) / 100
    return {'product_id': product_id, 'product': product, 'category': category}

@app.post('/purchase')
def add_purchase(user: User, product: Product):
    return {'user': user, 'product': product}

@app.post('/offer')
def add_offer(offer: Offer):
    return {'offer': offer}