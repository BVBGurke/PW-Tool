"""Kontogebundene, opt-in Verlaufschnittstellen."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ...models.records import AccountRecord
from ...schemas.history import HistoryListOutput
from ...services.registry import ServiceRegistry
from ..dependencies import get_current_account, get_services


router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryListOutput)
def history(
    account: AccountRecord = Depends(get_current_account),
    services: ServiceRegistry = Depends(get_services),
) -> HistoryListOutput:
    return HistoryListOutput.model_validate({"entries": services.history.list_for_account(account)})


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(
    entry_id: int,
    account: AccountRecord = Depends(get_current_account),
    services: ServiceRegistry = Depends(get_services),
) -> Response:
    services.history.delete(account, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
