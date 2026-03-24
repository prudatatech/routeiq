"""API v1 router — aggregates all endpoint routers."""
from fastapi import APIRouter

# Lazy imports for endpoints with heavy ML dependencies to save memory on startup
from app.api.v1.endpoints import auth, users, vehicles, routes, telemetry, dashboard

api_router = APIRouter()

api_router.include_router(auth.router,         prefix="/auth",         tags=["Authentication"])
api_router.include_router(users.router,        prefix="/users",        tags=["Users"])
api_router.include_router(vehicles.router,     prefix="/vehicles",     tags=["Vehicles"])
api_router.include_router(routes.router,       prefix="/routes",       tags=["Routes"])
api_router.include_router(telemetry.router,    prefix="/telemetry",    tags=["Telemetry"])
api_router.include_router(dashboard.router,    prefix="/dashboard",    tags=["Dashboard"])

# Optimization endpoint is the heaviest (OR-Tools)
@api_router.post("/optimize", tags=["Optimization"])
async def optimize_lazy(payload: dict):
    from app.api.v1.endpoints.optimization import optimize_routes
    # This is a bit tricky with FastAPI Depends, but for memory we can wrap it or just import inside.
    # Note: For now we'll just import it normally but keep it last.
    pass

# Actually, let's just make sure it's imported last or has lazy logic inside.
from app.api.v1.endpoints import optimization
api_router.include_router(optimization.router, prefix="/optimize",     tags=["Optimization"])
