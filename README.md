# Vehicle Defect Detection Equipment Health Monitoring System (VDDEHMS)

A reference systems engineering work package for a multi-subsystem condition monitoring platform that ensures the reliability and detection accuracy of inspection equipment on automotive vehicle assembly lines.

## Problem

Defect detection equipment on automotive assembly lines (vision systems, coordinate measuring machines, ultrasonic testers, torque tools, leak testers) degrades over time. Calibration drifts, transducers fail, false positive and false negative rates rise. When detection equipment misses defects, defective vehicles ship. When it raises false alarms, throughput drops and operators lose trust in the system. Today, equipment health is typically managed reactively through scheduled maintenance or post-failure response.

VDDEHMS continuously monitors the health and detection performance of defect detection equipment across an assembly line, surfaces predictive maintenance signals, and integrates with downstream maintenance and quality systems to enable proactive intervention before detection accuracy degrades to unacceptable levels.

## Scope

This repository contains the systems engineering work products for VDDEHMS, produced as a personal study in requirements engineering, architectural decomposition, and interface definition for complex systems-of-systems.

| Document | Purpose |
|----------|---------|
| [Concept of Operations](docs/01_CONOPS.md) | Operational environment, stakeholders, scenarios, system boundary |
| [System Requirements Specification](docs/02_REQUIREMENTS.md) | Functional, performance, interface, and non-functional requirements with verification methods |
| [System Architecture](docs/03_ARCHITECTURE.md) | Subsystem decomposition, cross-cutting concerns, technical risk register |
| [Interface Control Document](docs/04_INTERFACES.md) | External and internal interfaces with protocols, schemas, and verification approaches |

A minimal reference implementation of the PLC telemetry ingestion interface is provided in `src/edge/` to demonstrate that the interface specification is implementable.

## Repository Layout

```
vddehms/
├── docs/             Systems engineering work products
├── schemas/          JSON schemas referenced by interface contracts
├── proto/            Protocol Buffer definitions for internal interfaces
└── src/              Reference implementation
    ├── edge/         Edge node telemetry ingestion
    └── tests/        Contract tests for interfaces
```

## Status

Architecture and requirements documentation are stable. Reference implementation covers one external interface (PLC sensor telemetry via MQTT) with JSON Schema validation and a sample contract test.

## Author

Dipika Giri
