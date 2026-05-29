from fastapi import APIRouter
from app.api.v1.endpoints import users, webhooks

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(webhooks.router)