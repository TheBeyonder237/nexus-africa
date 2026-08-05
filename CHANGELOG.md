# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Automatic retries with exponential backoff and full jitter on transient
  failures (HTTP 429, 5xx and transport errors). Configurable per client via
  `max_retries` (default 3) and `backoff_factor` (default 0.5s); a
  `Retry-After` header is honoured when present. `max_retries=0` disables it.
- Regression tests asserting BaaS calls reach the BaaS host and never the gateway.

### Fixed

- BaaS resources now route to the `/baas-gateway` base URL instead of the
  payment gateway. Requests were previously sent to the wrong host because the
  `baas` flag was never propagated; a `_baas` class attribute on the base
  resources now carries it through every verb helper.
- Error parsing now reads the API's RFC 7807-style bodies: the exception
  `message` is taken from `title` (falling back to `message`) and `error_data`
  from `fieldErrors` (falling back to `errorData`). Previously errors surfaced
  as "Unknown error" because only `message`/`errorData` were read. Verified
  against a live sandbox 403 ("Ip not allowed").
- `raise_for_response` no longer crashes with `AttributeError` when the error
  body carries `code: null` (as validation errors do); it coalesces to
  `"UNKNOWN"`.
- Cash-in / cash-out now send the API-required `currencyCode` field (new
  `currency_code` parameter, default `"XAF"`). Collects previously failed with
  a 400 "Invalid data provided" (`currencyCode must not be blank`).
- `MobileMoneyDetails` now parses the `countryCode` field returned by the API
  while still sending `countryIso` on create (the two are asymmetric), so
  reading back a Mobile Money payment method no longer raises a validation
  error.

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
