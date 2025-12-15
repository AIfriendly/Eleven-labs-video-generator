# Architecture Documentation

> **Eleven Labs AI Video Generator** – CLI tool for automated video generation using AI services.

This document serves as the index to the comprehensive architecture documentation. For detailed decisions, patterns, and specifications, see the linked documents below.

---

## Quick Reference

| Aspect | Decision | Details |
|--------|----------|---------|
| **Architecture Pattern** | Hexagonal (Ports & Adapters) | [Core Decisions](./architecture/core-architectural-decisions.md) |
| **Package Manager** | `uv` | Fast, modern Python package manager |
| **CLI Framework** | Typer + Rich | Professional terminal experience |
| **API Integration** | Circuit breaker + retry + queue | 80% success rate requirement |
| **Configuration** | JSON in `~/.eleven-video/` | Environment variables for secrets |
| **Testing** | 40% unit / 30% integration / 30% E2E | ≥80% coverage required |

---

## Architecture Documents

### 📋 Core Documents

| Document | Purpose |
|----------|---------|
| [**Core Architectural Decisions**](./architecture/core-architectural-decisions.md) | Critical technology choices and consensus decisions |
| [**Project Structure & Boundaries**](./architecture/project-structure-boundaries.md) | Directory structure, component boundaries, file organization |
| [**Implementation Patterns**](./architecture/implementation-patterns-consistency-rules.md) | Naming conventions, error handling, communication patterns |

### 🔍 Analysis & Rationale

| Document | Purpose |
|----------|---------|
| [**Project Context**](./architecture/project-context.md) | Project overview and input document analysis |
| [**Project Context Analysis**](./architecture/project-context-analysis.md) | Requirements, constraints, cross-cutting concerns |
| [**Architecture Decision Records**](./architecture/architecture-decision-records.md) | Multi-persona decision analysis |
| [**First Principles Architecture**](./architecture/first-principles-architecture.md) | Fundamental truths and stripped-down architecture |
| [**Tree of Thoughts Analysis**](./architecture/recommended-architecture-tree-of-thoughts-analysis.md) | Architecture option evaluation |

### ⚠️ Risk & Validation

| Document | Purpose |
|----------|---------|
| [**Risk Assessment**](./architecture/risk-assessment.md) | Technical, security, and product risks |
| [**Pre-Mortem Analysis**](./architecture/pre-mortem-analysis-potential-failure-scenarios.md) | Potential failure scenarios and mitigations |
| [**Architecture Validation Results**](./architecture/architecture-validation-results.md) | Coherence, coverage, and readiness validation |

### 🛠️ Implementation Guidance

| Document | Purpose |
|----------|---------|
| [**Starter Template Evaluation**](./architecture/starter-template-evaluation.md) | Technology selection rationale |
| [**Cross-Functional Decisions**](./architecture/cross-functional-architecture-decisions.md) | Joint recommendations across concerns |
| [**Full Index**](./architecture/index.md) | Complete table of contents with section links |

---

## Key Architecture Decisions

### 1. Hexagonal Architecture
Clean separation between domain logic (orchestrator) and infrastructure (API adapters, processing). Enables testability and future extensibility.

### 2. API Integration Strategy
- **HTTPX** for sync/async API calls
- **Circuit breaker** pattern for fault tolerance
- **Exponential backoff** for retries
- **Queue management** for rate limiting

### 3. Security Model
- API keys stored in `.env` files with `600` permissions
- No credentials logged or exposed
- Configuration in user's home directory

### 4. Terminal Interface
- **Rich** library for professional displays, progress bars, tables
- **Typer** for CLI command structure
- Real-time monitoring of API usage and progress

---

## Package Management

This project uses `uv` as the Python package manager.

### Installation

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Usage

```bash
uv pip install -e ".[dev]"
```

---

## Related Documents

- [Product Requirements (PRD)](./prd.md)
- [Epics & Stories](./epics.md)
- [UX Design](./ux-design.md)
