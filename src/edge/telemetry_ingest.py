"""
Edge Node telemetry ingestion reference implementation.

Implements the ingress side of ICD-EXT-001: PLC Telemetry Ingestion.
This module shows that the interface contract in schemas/plc_telemetry.v1.json
is implementable and that schema validation can be enforced at the edge.

A production deployment would replace InMemoryTelemetrySink with a forwarder
to the Central Server over gRPC per ICD-INT-001.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    from jsonschema import Draft202012Validator
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "plc_telemetry.v1.json"


@dataclass
class TelemetrySample:
    """A single decoded telemetry sample for downstream processing."""
    equipment_id: str
    timestamp: datetime
    metric: str
    value: float


@dataclass
class IngestionResult:
    """Result of ingesting a single payload."""
    accepted: list[TelemetrySample] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)


class SchemaValidator:
    """Validates payloads against the PLC telemetry JSON schema."""

    def __init__(self, schema_path: Path = SCHEMA_PATH) -> None:
        if not _HAS_JSONSCHEMA:
            raise RuntimeError(
                "jsonschema is required for schema validation. "
                "Install with: pip install jsonschema"
            )
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        self._validator = Draft202012Validator(schema)

    def errors(self, payload: dict) -> list[str]:
        return [e.message for e in sorted(self._validator.iter_errors(payload), key=lambda e: e.path)]


class TelemetryIngestor:
    """
    Edge node ingestion entry point.

    A real deployment would wrap this in an MQTT subscriber. For
    testability, this class exposes a synchronous `ingest_payload` method
    that takes a JSON string and returns a structured IngestionResult.
    """

    def __init__(self, validator: SchemaValidator | None = None) -> None:
        self._validator = validator or SchemaValidator()

    def ingest_payload(self, raw: str) -> IngestionResult:
        result = IngestionResult()

        # 1. Parse
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            result.rejected.append(f"invalid_json: {e.msg}")
            return result

        # 2. Validate against schema
        errors = self._validator.errors(payload)
        if errors:
            result.rejected.extend(f"schema_error: {msg}" for msg in errors)
            return result

        # 3. Decode samples
        equipment_id = payload["equipment_id"]
        timestamp = _parse_timestamp(payload["timestamp"])
        for sample in payload["samples"]:
            result.accepted.append(
                TelemetrySample(
                    equipment_id=equipment_id,
                    timestamp=timestamp,
                    metric=sample["metric"],
                    value=float(sample["value"]),
                )
            )
        return result


def _parse_timestamp(ts: str) -> datetime:
    # RFC 3339 with optional trailing Z
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


__all__ = [
    "IngestionResult",
    "SchemaValidator",
    "TelemetryIngestor",
    "TelemetrySample",
]
