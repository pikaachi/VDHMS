# 04. Interface Control Document (ICD)

## 1. Purpose

This document specifies the external and internal interfaces of VDDEHMS. Each interface entry includes parties, protocol, data format, update rate, latency budget, error handling, and security posture. Each external interface satisfies a corresponding interface requirement in the [System Requirements Specification](02_REQUIREMENTS.md).

## 2. Interface Index

| Interface ID | Title | Parties | Protocol |
|--------------|-------|---------|----------|
| ICD-EXT-001 | PLC Telemetry Ingestion | Detection Equipment PLC → Edge Node | MQTT/TLS |
| ICD-EXT-002 | Vision System Metrics Ingestion | Vision Station → Edge Node | HTTPS REST |
| ICD-EXT-003 | CMMS Work Order Publication | Central Server → CMMS | HTTPS REST |
| ICD-EXT-004 | DMS Re-inspection Flag | Central Server → DMS | Kafka |
| ICD-EXT-005 | MES Production Context | MES → Central Server | HTTPS REST |
| ICD-INT-001 | Edge to Central Telemetry and Alert Stream | Edge Node → Central Server | gRPC/mTLS |
| ICD-INT-002 | Operator Console to Central API | Browser → Central Server | HTTPS REST |

## 3. External Interfaces

### 3.1 ICD-EXT-001: PLC Telemetry Ingestion

| Attribute | Specification |
|-----------|---------------|
| Source | Detection equipment PLC |
| Sink | Edge Node MQTT broker |
| Protocol | MQTT 3.1.1 over TLS 1.2 or higher |
| Topic pattern | `plant/{plant_id}/line/{line_id}/station/{station_id}/equipment/{equipment_id}/telemetry` |
| Data format | JSON, schema in `schemas/plc_telemetry.v1.json` |
| Update rate | 1 to 10 Hz per equipment, aggregate up to 1,000 samples per second per edge node |
| Latency budget | Less than 500 ms from PLC publish to edge ingest |
| Delivery semantics | At-least-once (MQTT QoS 1) |
| Error handling | Malformed payloads logged and dropped; loss-of-signal alarms after 3 consecutive missed publish periods |
| Security | Mutual TLS with per-equipment client certificates |

**Sample payload:**
```json
{
  "schema_version": "1.0",
  "equipment_id": "TORQUE-L3-S07",
  "timestamp": "2026-06-30T14:21:00.123Z",
  "samples": [
    { "metric": "applied_torque_nm", "value": 42.7 },
    { "metric": "angle_deg", "value": 178.4 },
    { "metric": "transducer_drift_pct", "value": 0.12 }
  ]
}
```

### 3.2 ICD-EXT-002: Vision System Metrics Ingestion

| Attribute | Specification |
|-----------|---------------|
| Source | Vision inspection station |
| Sink | Edge Node REST endpoint |
| Protocol | HTTPS REST |
| Endpoint | `POST /v1/metrics` on edge node |
| Data format | JSON |
| Update rate | One batch per inspection cycle |
| Latency budget | Less than 2 seconds from inspection complete to edge receipt |
| Error handling | HTTP 4xx for malformed input, 5xx for transient errors; client retries with exponential backoff up to 5 attempts |
| Security | Mutual TLS |

### 3.3 ICD-EXT-003: CMMS Work Order Publication

| Attribute | Specification |
|-----------|---------------|
| Source | Central Server |
| Sink | CMMS |
| Protocol | HTTPS REST |
| Endpoint | `POST {cmms_base_url}/work-orders` |
| Data format | JSON aligned with CMMS WorkOrder v2 schema |
| Update rate | Event driven, expected less than 100 per day per plant |
| Idempotency | Idempotency-Key header derived from `equipment_id + root_cause_hash` |
| Error handling | Persistent queue with retry on 5xx; dead-letter after 24 hours and operator alert |
| Security | OAuth2 client credentials grant |

### 3.4 ICD-EXT-004: DMS Re-inspection Flag

| Attribute | Specification |
|-----------|---------------|
| Source | Central Server |
| Sink | DMS |
| Protocol | Apache Kafka |
| Topic | `vddehms.reinspection.flags.v1` |
| Data format | Avro, schema registered in plant Schema Registry |
| Update rate | Event driven |
| Ordering | Partitioned by `equipment_id` to preserve per-equipment ordering |
| Delivery semantics | At-least-once; consumer dedupes on `flag_id` |
| Error handling | Producer retries on broker unavailable; metrics emitted for failed publishes |
| Security | SASL/SCRAM, ACL-restricted topic |

### 3.5 ICD-EXT-005: MES Production Context (consumed)

| Attribute | Specification |
|-----------|---------------|
| Source | MES |
| Sink | Central Server |
| Protocol | HTTPS REST |
| Purpose | Pull current line, station, and production unit context to attach to alerts |
| Update rate | Pull on alert generation, with short-lived cache |
| Error handling | Alert is generated without MES context if pull fails; context attached asynchronously when MES recovers |
| Security | Mutual TLS, plus signed JWT for caller identity |

## 4. Internal Interfaces

### 4.1 ICD-INT-001: Edge to Central Telemetry and Alert Stream

| Attribute | Specification |
|-----------|---------------|
| Source | Edge Node |
| Sink | Central Server |
| Protocol | gRPC over mutual TLS |
| Services | `EdgeToCentral.StreamTelemetry`, `EdgeToCentral.RaiseAlert` |
| Data format | Protocol Buffers, defined in `proto/edge_to_central.v1.proto` |
| Resilience | Edge buffers up to one hour locally on connection loss; replays on reconnect in original order |
| Security | mTLS with per-edge client certificates issued by plant CA |

### 4.2 ICD-INT-002: Operator Console to Central API

| Attribute | Specification |
|-----------|---------------|
| Source | Browser-based operator console |
| Sink | Central Server REST API |
| Protocol | HTTPS REST |
| Authentication | Plant SSO via OpenID Connect, session bound JWT |
| Authorization | RBAC roles: operator, maintenance, quality_engineer, supervisor, admin |
| Error handling | Standard HTTP status codes, machine-readable error envelope |

## 5. Interface Verification

Each interface is verified per the methods in [Requirements Section 6](02_REQUIREMENTS.md). Contract tests are maintained in `src/tests/` and exercised in CI on every change to the corresponding schema or proto definition.

## 6. Change Management

Interface schema versions are immutable once published. Breaking changes are introduced as a new schema version (for example `plc_telemetry.v2.json`). Both versions are supported during a documented deprecation window of no less than two release cycles.
