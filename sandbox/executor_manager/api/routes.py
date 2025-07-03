from fastapi import APIRouter

from api.handlers import healthz_handler, run_code_handler

router = APIRouter()

router.get("/healthz")(healthz_handler)
router.post("/run")(run_code_handler)