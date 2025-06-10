from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL="mongodb://127.0.0.1?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database('fastapi')
product_collection = db.get_collection('product')
seller_collection = db.get_collection('seller')
