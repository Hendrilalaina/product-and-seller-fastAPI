from fastapi import FastAPI
from pydantic import BaseModel

class Profile(BaseModel):
    name: str
    email: str
    age: int

class Product(BaseModel):
    name: str
    price: int
    discount: int
    discount_price: float

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

@app.post('/adduser')
def add_profile(profile: Profile):
    return profile

@app.post('/addproduct/{product_id}')
def add_product(product: Product, product_id: int, category: str):
    product.discount_price = product.price \
        - (product.price * product.discount) / 100
    return {'product_id': product_id, 'product': product, 'category': category}