## Security

 - [ ] S063 - Secret Management : Centralise secrets via env vars and optional file-based secrets; validate at startup and redact in logs.

 - [ ] S064 - JWKS & Key Rotation : Support JWKS URL retrieval/caching with `kid`-based key selection to enable seamless rotation.

## Developer Experience

 - [ ] S065 - CLI Scaffolding : Add `flarchitect` CLI (init app, generate demo model, manage config, print OpenAPI).

 - [ ] S066 - Pre-commit Quality Gates : ruff + mypy (strict), bandit/safety, coverage thresholds, and CodeQL; ship pre-commit config.

## Architecture & Extensibility

 - [ ] S080 - Plugin Examples Gallery : Curated examples of common plugins (audit, metrics, multi-tenancy) with code and tests.

 - [ ] S068 - Signals/Event Bus : Emit CRUD signals (e.g., with blinker) for decoupled listeners and extensions.

## API & Spec

 - [ ] S069 - Deterministic Spec : Stable operationIds and deterministic ordering; collision guards for re-registration.

 - [ ] S070 - Schema Filters & Metadata : Per-field include/exclude, examples and deprecation markers; override descriptions.

  - [ ] S088 - Route Naming Strategy : Add flexible relation-route naming strategy (model|relationship|auto) with per-model overrides and alias map; ensure deterministic operationIds.

## Performance

 - [ ] S071 - Conditional Requests : ETag/Last-Modified support with If-None-Match/If-Modified-Since handling.

 - [ ] S072 - Cache Controls : Configurable `Cache-Control` headers and microcaching for generated spec responses.

## Features

 - [ ] S073 - Bulk Operations : Batch create/update/delete with transactional semantics and partial failure reporting.

 - [ ] S074 - Webhooks : Outbound webhook subscriptions on CRUD events with retries and HMAC signing.

  - [ ] S089 - Relationship Aliases : Expose per-relationship aliasing via `Meta.relation_route_map` with validation and documentation examples.

## Testing & Quality

 - [ ] S075 - Property-Based Tests : Hypothesis-driven CRUD roundtrip tests across generated models.

 - [ ] S076 - Performance Benchmarks : Baseline latency/throughput tests for core endpoints and budgets.

  - [ ] S082 - WS Endpoint Tests : Add integration tests for optional WebSocket endpoint behind `flask_sock` when dependency is available.

## Documentation

 - [ ] S077 - Security Hardening Guide : Deployment checklist (secrets, algorithms, CORS, cookies) and incident response notes.

 - [ ] S079 - RBAC & ABAC Guide : Role- and attribute-based access control patterns with examples and best practices.

## Complete

 - [x] S013 - JWT Hardening : Leeway, aud/iss, allowed algorithms, RS256 key pairs supported and documented.

 - [x] S014 - Token Rotation : Implemented refresh token rotation (single-use), revocation (deny-list), and last-used auditing with tests and docs.

 - [x] S078 - Auth Cookbook : JWT, Basic and API key patterns; role mapping examples; multi-tenant considerations.

 - [x] S067 - Plugin Hooks : Formal pre/post hooks for request lifecycle, model ops, and schema build with stable signatures.

 - [x] S081 - Coverage Budget : Raise coverage above 90% by adding focused tests for responses, logging, core utils, websockets bus, and schema models. Excluded optional `init_websockets` from coverage accounting.

 - [x] S083 - Docs Spec Route : Serve docs JSON at `/docs/apispec.json` and add `API_DOCS_SPEC_ROUTE` setting; updated tests and documentation accordingly.

 - [x] S084 - Config Docs: Document `DOCUMENTATION_URL_PREFIX` default and usage in the configuration reference; ensures discoverability of the docs prefix setting.

 - [x] S085 - Meta Requirement Docs : Make it explicit that models without a `Meta` inner class are not auto-registered for routes or documentation; add warnings to README and docs.

 - [x] S086 - Optional Tag Grouping : Document that `Meta.tag` and `Meta.tag_group` are optional; ensure generator defaults to a safe tag when absent.

 - [x] S087 - Relation Key Endpoints : Use relation attribute key in relation routes and endpoint names to avoid collisions when multiple FKs target the same model; initial compatibility via config, later superseded by `API_RELATION_ROUTE_NAMING` with richer controls; docs/tests updated.

 - [x] S090 - 403 Role Error Enrichment : Enrich 403 responses on role mismatch with required roles, matching semantics, request context, resolved config key, and best‑effort user/lookup info; driven by `API_ROLE_MAP`.

  - [x] S091 - Auto Auth Refresh Route : Auto-register POST `/auth/refresh` when JWT is enabled; configurable via `API_AUTO_AUTH_ROUTES` and `API_AUTH_REFRESH_ROUTE`; idempotent registration; tests and docs added.
