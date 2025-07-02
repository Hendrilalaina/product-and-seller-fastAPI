import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.product import router as product_router
from router.auth import router as auth_router

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

app.include_router(product_router)
app.include_router(auth_router)