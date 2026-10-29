"""Central API router — mounts all v1 sub-routers."""
from fastapi import APIRouter

from app.api.v1 import auth, products, categories, deals, users, ai, admin

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(categories.router)
api_router.include_router(deals.router)
api_router.include_router(users.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
