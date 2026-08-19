"""Minimaler, nicht sensitiver Betriebsstatus."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ...schemas.common import HealthOutput


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthOutput)
def health(request: Request) -> HealthOutput:
    return HealthOutput(status="ok", lan_enabled=bool(request.app.state.settings.lan_enabled))


@router.get("/readiness", response_model=HealthOutput)
def readiness(request: Request) -> HealthOutput:
    return HealthOutput(status="ready", lan_enabled=bool(request.app.state.settings.lan_enabled))
