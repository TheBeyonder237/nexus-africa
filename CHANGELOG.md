# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- BaaS resources now route to the `/baas-gateway` base URL instead of the
  payment gateway. Requests were previously sent to the wrong host because the
  `baas` flag was never propagated; a `_baas` class attribute on the base
  resources now carries it through every verb helper.

### Added

- Regression tests asserting BaaS calls reach the BaaS host and never the gateway.

## [0.1.0] - 2026-07-27

### Added

- `NexusClient` (sync) and `AsyncNexusClient` (async, httpx) with context-manager support.
- Pydantic v2 models for all request/response objects (snake_case Python, camelCase API aliases).
- Typed exception hierarchy (`PM-`, `TI-`, `verif-`, `gtw-`, `GE-`, `BAL-`, `TS-`), including `IdempotencyConflict`.
- Payment Methods: `create`, `create_mobile_money`, `create_merchant`, `list`, `get`.
- Transaction Intents: `cash_in`, `cash_out`, `get`, `list`, `confirm`, `cancel`.
- Balances: `get`.
- Sessions: `create` (hosted payment link).
- Nexus Flow (marketplace fund distribution) support on cash-in.
- Webhook: `verify_signature` + `verify_and_parse` with HMAC-SHA512 replay protection.
- BaaS skeleton: KYC onboarding, party management, virtual card issuance/freeze/cancel.
- 34 tests covering exceptions, webhook, payment methods, intents and the async client.

[0.1.0]: https://github.com/TheBeyonder237/nexus-africa/releases/tag/v0.1.0
