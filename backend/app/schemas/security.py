"""Verträge für die selbstbezogene Hash-Demo und Laufzeitmetadaten."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HashDemoInput(BaseModel):
    length: int = Field(default=32, ge=16, le=256)
    charset: Literal["normal", "complete"] = "complete"


class HashDemoOutput(BaseModel):
    algorithm: Literal["scrypt"]
    n: int
    r: int
    p: int
    salt_bytes: int
    output_bytes: int
    duration_ms: float
    verified: bool
    notice: str


class CudaCapabilityOutput(BaseModel):
    used_for_passwords: bool
    used_for_hash_demo: bool
    status: str


class CapabilityOutput(BaseModel):
    system: str
    architecture: str
    password_generation_path: Literal["os-csprng-cpu"]
    cuda: CudaCapabilityOutput
