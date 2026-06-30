"""
Contract tests for ICD-EXT-001 PLC Telemetry Ingestion.

These tests verify that the edge ingestion implementation accepts
payloads conforming to schemas/plc_telemetry.v1.json and rejects
payloads that violate the contract. They are the executable
counterpart to the interface specification.

Run with: pytest src/tests/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from src.edge.telemetry_ingest import TelemetryIngestor  # noqa: E402


@pytest.fixture
def ingestor() -> TelemetryIngestor:
    return TelemetryIngestor()


def _valid_payload() -> dict:
    return {
        "schema_version": "1.0",
        "equipment_id": "TORQUE-L3-S07",
        "timestamp": "2026-06-30T14:21:00.123Z",
        "samples": [
            {"metric": "applied_torque_nm", "value": 42.7},
            {"metric": "angle_deg", "value": 178.4},
            {"metric": "transducer_drift_pct", "value": 0.12},
        ],
    }


class TestValidPayloads:
    def test_canonical_payload_is_accepted(self, ingestor: TelemetryIngestor) -> None:
        result = ingestor.ingest_payload(json.dumps(_valid_payload()))
        assert result.rejected == []
        assert len(result.accepted) == 3
        assert result.accepted[0].equipment_id == "TORQUE-L3-S07"
        assert result.accepted[0].metric == "applied_torque_nm"
        assert result.accepted[0].value == pytest.approx(42.7)


class TestSchemaViolations:
    def test_missing_required_field_is_rejected(self, ingestor: TelemetryIngestor) -> None:
        payload = _valid_payload()
        del payload["equipment_id"]
        result = ingestor.ingest_payload(json.dumps(payload))
        assert result.accepted == []
        assert any("equipment_id" in msg for msg in result.rejected)

    def test_unknown_top_level_field_is_rejected(self, ingestor: TelemetryIngestor) -> None:
        payload = _valid_payload()
        payload["unexpected"] = "value"
        result = ingestor.ingest_payload(json.dumps(payload))
        assert result.accepted == []
        assert result.rejected != []

    def test_invalid_equipment_id_format_is_rejected(self, ingestor: TelemetryIngestor) -> None:
        payload = _valid_payload()
        payload["equipment_id"] = "lowercase-not-allowed"
        result = ingestor.ingest_payload(json.dumps(payload))
        assert result.accepted == []
        assert result.rejected != []

    def test_empty_samples_array_is_rejected(self, ingestor: TelemetryIngestor) -> None:
        payload = _valid_payload()
        payload["samples"] = []
        result = ingestor.ingest_payload(json.dumps(payload))
        assert result.accepted == []
        assert result.rejected != []


class TestMalformedInput:
    def test_invalid_json_is_rejected(self, ingestor: TelemetryIngestor) -> None:
        result = ingestor.ingest_payload("{ not valid json")
        assert result.accepted == []
        assert result.rejected != []
        assert "invalid_json" in result.rejected[0]
