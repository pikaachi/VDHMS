# 02. System Requirements Specification

## 1. Introduction

This document specifies the functional, performance, interface, and non-functional requirements for VDDEHMS. Each requirement uses "shall" language and includes a verification method.

**Verification Methods:**
- **I** Inspection: visual or document review
- **A** Analysis: modeling, simulation, or calculation
- **D** Demonstration: operate the system to observe intended behavior
- **T** Test: formal pass or fail measurement against defined criteria

Requirements derive from the stakeholder concerns in [CONOPS Section 4](01_CONOPS.md) and the operational scenarios in [CONOPS Section 5](01_CONOPS.md).

## 2. Functional Requirements

### 2.1 Data Acquisition

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-FUN-001 | The system shall ingest health telemetry from supported defect detection equipment classes including vision, coordinate measuring machines, ultrasonic testers, torque tools, and leak testers. | T |
| SYS-FUN-002 | The system shall associate every telemetry sample with an equipment identifier, station identifier, line identifier, and timestamp. | T |
| SYS-FUN-003 | The system shall persist raw telemetry for a configurable retention period of at least 90 days. | T |
| SYS-FUN-004 | The system shall continue ingestion at the edge during loss of connectivity to the central server and replay buffered data on reconnect with original ordering preserved. | D |

### 2.2 Health Evaluation

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-FUN-010 | The system shall compute per-equipment health scores derived from telemetry, calibration baselines, and detection outcome statistics. | A, T |
| SYS-FUN-011 | The system shall detect drift in detection accuracy by comparing recent performance against a rolling baseline window. | A, T |
| SYS-FUN-012 | The system shall classify alerts into three severity tiers: Tier 1 informational, Tier 2 actionable, Tier 3 critical. | D |

### 2.3 Alerting and Workflow

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-FUN-020 | The system shall notify the appropriate stakeholder role within 60 seconds of an alert being raised. | T |
| SYS-FUN-021 | The system shall publish maintenance work order requests to CMMS for Tier 2 and Tier 3 alerts. | T |
| SYS-FUN-022 | The system shall flag affected production units to DMS for re-inspection when a Tier 3 sensor failure is detected. | T |
| SYS-FUN-023 | The system shall allow authorized users to acknowledge, defer, or close alerts via the operator console. | D |

### 2.4 Calibration and Configuration

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-FUN-030 | The system shall allow maintenance technicians to record calibration events and update equipment baselines. | D |
| SYS-FUN-031 | The system shall support configuration of equipment-specific performance thresholds without code change or redeployment. | D |

### 2.5 Historical Query

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-FUN-040 | The system shall support time-bounded queries of telemetry, alerts, and calibration history filtered by equipment, station, or line. | D |

## 3. Performance Requirements

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-PRF-001 | The system shall ingest telemetry at a sustained rate of at least 1,000 samples per second per edge node. | T |
| SYS-PRF-002 | The system shall raise Tier 3 alerts within 5 seconds of the triggering telemetry event. | T |
| SYS-PRF-003 | Operator console screens shall load within 2 seconds at the 95th percentile under nominal plant load. | T |

## 4. Interface Requirements

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-IFC-001 | The system shall consume PLC telemetry via MQTT over TLS in accordance with [ICD-EXT-001](04_INTERFACES.md). | T |
| SYS-IFC-002 | The system shall consume vision system performance metrics via REST in accordance with [ICD-EXT-002](04_INTERFACES.md). | T |
| SYS-IFC-003 | The system shall publish work order requests to CMMS via REST in accordance with [ICD-EXT-003](04_INTERFACES.md). | T |
| SYS-IFC-004 | The system shall publish unit re-inspection flags to DMS via Kafka in accordance with [ICD-EXT-004](04_INTERFACES.md). | T |
| SYS-IFC-005 | The system shall implement the edge to central telemetry and alert stream in accordance with [ICD-INT-001](04_INTERFACES.md). | I |

## 5. Non-Functional Requirements

### 5.1 Availability

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-NFR-001 | The system shall achieve 99.5% availability per calendar month, excluding planned maintenance windows. | A |

### 5.2 Security

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-NFR-010 | The system shall authenticate all external interface clients using mutual TLS or equivalent. | I, T |
| SYS-NFR-011 | The system shall enforce role-based access control for the operator console covering operator, maintenance, quality engineer, supervisor, and admin roles. | T |
| SYS-NFR-012 | The system shall log all configuration changes and alert acknowledgments to an append-only audit trail. | I |

### 5.3 Maintainability

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-NFR-020 | The system shall expose health endpoints suitable for plant IT monitoring tools. | I |
| SYS-NFR-021 | The system shall support rolling updates of edge nodes without disrupting central server operation. | D |

### 5.4 Safety

| ID | Requirement | Verification |
|----|-------------|--------------|
| SYS-NFR-030 | The system shall not actuate any plant floor control function; the system is advisory only. | I |

## 6. Verification Approach

Verification is performed at three levels:

1. **Subsystem** acceptance prior to integration
2. **Integration** verification of cross-subsystem behavior
3. **Operational acceptance** in plant environment prior to production cutover

A representative excerpt from the verification matrix follows. The full matrix is maintained in the requirements management tool.

| Requirement | Method | Phase |
|-------------|--------|-------|
| SYS-FUN-001 | T | Subsystem |
| SYS-FUN-020 | T | Integration |
| SYS-PRF-001 | T | Subsystem |
| SYS-PRF-002 | T | Integration |
| SYS-NFR-001 | A | Operational acceptance |
| SYS-NFR-030 | I | Design review |
