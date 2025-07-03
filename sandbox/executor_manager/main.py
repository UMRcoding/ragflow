from api.routes import router as api_router
from core.config import init
from fastapi import FastAPI
from services.limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(lifespan=init())
app.include_router(api_router)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
