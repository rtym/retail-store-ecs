# BG-2: End-to-end shopping journey works

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Statement**: Shoppers (ST-5) need to browse, search, fill a cart and check out so that every completed checkout produces a stored order — the storefront's functional purpose.
- **Primary stakeholder**: ST-5 — Shopper (see [stakeholders](../stakeholders.md))
- **SEI business-goal category**: product quality
- **Measure of success**: Checkout success ratio and order persistence (no metric exists today — see OQA-1).
- **Priority**: high
- **Status**: at risk

## Context

Derived from the five deployed services (ui, catalog, carts, checkout, orders) and their wiring (`RETAIL_UI_ENDPOINTS_*`, `RETAIL_CHECKOUT_ENDPOINTS_ORDERS`).

## Supported by

- Use cases: [UC-1](../use-cases/UC-1.md), [UC-2](../use-cases/UC-2.md), [UC-3](../use-cases/UC-3.md), [UC-4](../use-cases/UC-4.md), [UC-5](../use-cases/UC-5.md)
- Quality attribute scenarios: [AQA-1](../quality-attributes/AQA-1.md), [AQA-2](../quality-attributes/AQA-2.md), [PQA-1](../quality-attributes/PQA-1.md), [SCQA-1](../quality-attributes/SCQA-1.md)

## Notes

Derived from function, not from a stated goal.
