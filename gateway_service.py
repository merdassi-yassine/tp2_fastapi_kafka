from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="Gateway")

USERS_SERVICE_URL = "http://localhost:8000"
PRODUCTS_SERVICE_URL = "http://localhost:8001"


@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=15.0)
            return response.json()
        except httpx.ConnectError:
            return {"error": "Service unavailable"}


@app.get("/api/products/{user_id}")
async def get_products(user_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PRODUCTS_SERVICE_URL}/products/{user_id}", timeout=15.0)
            return response.json()
        except httpx.ConnectError:
            return {"error": "Service unavailable"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
