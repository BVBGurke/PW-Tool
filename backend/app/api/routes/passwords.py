"""Geschützte CSPRNG-Passworterzeugungsroute."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ...middleware.rate_limit import MemoryRateLimiter
from ...models.records import AccountRecord
from ...schemas.passwords import GenerationInput, GenerationOutput
from ...services.registry import ServiceRegistry
from ..dependencies import client_key, enforce_limit, get_current_account, get_limiter, get_services


router = APIRouter(prefix="/passwords", tags=["passwords"])


@router.post("/generate", response_model=GenerationOutput)
def generate(
    payload: GenerationInput,
    request: Request,
    account: AccountRecord = Depends(get_current_account),
    services: ServiceRegistry = Depends(get_services),
    limiter: MemoryRateLimiter = Depends(get_limiter),
) -> GenerationOutput:
    enforce_limit(limiter, f"generate:{account.id}:{client_key(request)}", 60, 60)
    return GenerationOutput.model_validate(
        services.passwords.generate(account, payload.length, payload.count, payload.charset, payload.save_history)
    )
