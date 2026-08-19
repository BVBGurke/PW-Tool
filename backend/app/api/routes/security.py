"""Begrenzte Sicherheitsdemo und harmlose Laufzeit-Capability-Informationen."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...models.records import AccountRecord
from ...schemas.security import CapabilityOutput, HashDemoInput, HashDemoOutput
from ...services.registry import ServiceRegistry
from ..dependencies import get_current_account, get_services


router = APIRouter(prefix="/security", tags=["security"])


@router.post("/hash-demo", response_model=HashDemoOutput)
def hash_demo(
    payload: HashDemoInput,
    account: AccountRecord = Depends(get_current_account),
    services: ServiceRegistry = Depends(get_services),
) -> HashDemoOutput:
    del account
    return HashDemoOutput.model_validate(services.hash_demo.run(payload.length, payload.charset))


@router.get("/capabilities", response_model=CapabilityOutput)
def capabilities(
    account: AccountRecord = Depends(get_current_account),
    services: ServiceRegistry = Depends(get_services),
) -> CapabilityOutput:
    del account
    return CapabilityOutput.model_validate(services.capability.status())
