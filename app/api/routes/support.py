from fastapi import APIRouter

from app.models.support import CheckInRequest, CheckInResponse
from app.services.support import build_support_response

router = APIRouter(prefix="/v1/support", tags=["support"])


@router.post("/check-in", response_model=CheckInResponse)
def check_in(payload: CheckInRequest) -> CheckInResponse:
    return build_support_response(payload)
