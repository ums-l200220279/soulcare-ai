from fastapi import APIRouter, Header, HTTPException, Request

from app.models.support import CheckInRequest, CheckInResponse
from app.core.runtime import payload_hash
from app.services.support import build_support_response

router = APIRouter(prefix="/v1/support", tags=["support"])


@router.post("/check-in", response_model=CheckInResponse)
def check_in(
    payload: CheckInRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> CheckInResponse:
    payload_data = payload.model_dump()
    if idempotency_key:
        payload_digest = payload_hash(payload_data)
        try:
            cached_response = request.app.state.idempotency_store.get(idempotency_key, payload_digest)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if cached_response:
            return CheckInResponse(**cached_response)
        response = build_support_response(payload)
        response_data = response.model_dump()
        request.app.state.idempotency_store.set(idempotency_key, payload_digest, response_data)
        return response
    return build_support_response(payload)
