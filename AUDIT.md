# HappyCana — Production Readiness Audit

**Repo:** zicojojo/happycana
**Commit audited:** `5eebf8c66304b9c2ee7fdccba223740389655272`
**Date:** 2026-09-04
**Scope:** Backend (Django) + Frontend (Next.js)

This is a point-in-time review, not a full penetration test or formal security audit. It covers configuration, dependency hygiene, auth/payment handling, and test coverage across both halves of the repo.

---

## Summary

| Severity | Count |
|---|---|
| Blocker | 4 |
| Minor | 2 |
| Solid (no action needed) | 8 |

**Bottom line:** the foundations are good — environment-gated settings, real payment gateway integrations with verified webhooks, no committed secrets, strict TypeScript, backend test coverage. The gaps are mostly things that get found and abused fast if shipped as-is, not deep architectural problems. Rate limiting is the one I'd fix before anything else.

---

## Blockers

### 1. No rate limiting on any endpoint
`Backend/requirements/production.txt` lists `django-ratelimit` under a `# Security` comment, explicitly noted for "rate limiting on sensitive endpoints" — but it is never imported or applied anywhere in the codebase (`grep -rn "ratelimit" Backend/apps Backend/core Backend/config` returns nothing).

**Impact:** login, checkout, and webhook endpoints currently have zero throttling. Brute-force credential stuffing and checkout abuse are both live risks.

**Fix:** apply `django_ratelimit.decorators.ratelimit` (or DRF's `DEFAULT_THROTTLE_CLASSES`/`DEFAULT_THROTTLE_RATES`) to at minimum: login, password reset, registration, and checkout/order-creation views.

### 2. Dependencies are almost entirely unpinned
`Backend/requirements/base.txt` — 42 lines, only 2 use `==`. Everything else (`Django`, `djangorestframework`, `channels`, etc.) has no version pin.

**Impact:** a fresh `pip install -r requirements.txt` on any future deploy can silently pull in a breaking major version with no warning — this is the kind of thing that breaks a production deploy at 2am for no code-side reason.

**Fix:** pin at least major.minor for every package (`Django>=5.0,<5.1` style, or fully pinned with a lockfile via `pip-compile`/`uv`).

### 3. No frontend test coverage
`grep` for `*.test.*`/`*.spec.*` under `frontend/src` returns zero files, and `package.json` has no `test` script at all.

**Impact:** checkout flow, cart logic, and the WebSocket-driven chat (`useChat.ts`, `useWebSocket.ts`) — all client-side, all stateful, all currently changing hands between multiple contributors — have no automated safety net.

**Fix:** at minimum, add coverage for the checkout flow and the WebSocket reconnect/auth-error logic in `useChat.ts`, since that's the highest-complexity client state in the app.

### 4. No idempotency key on payment intent creation
`Backend/apps/payments/gateways/stripe.py` — `create_payment_intent()` has no visible idempotency-key handling.

**Impact:** a client-side retry (double-click, network blip, mobile app backgrounding) can risk creating duplicate PaymentIntents / duplicate charges for the same order.

**Fix:** pass `idempotency_key=` (keyed off the order ID) on the Stripe API call.

---

## Minor

### 5. No CI configuration in-repo
No `.github/workflows`, `.gitlab-ci.yml`, or equivalent found in the repository. May live in a separate deployment pipeline — worth confirming lint/tsc/tests actually run somewhere before merge, since they clearly aren't enforced automatically on this repo (see the ESLint/`tsc` issues fixed manually in recent commits).

### 6. Wide-open image remote pattern
`frontend/next.config.ts`:
```ts
remotePatterns: [
  { protocol: "https", hostname: "**" },
  ...
]
```
Any HTTPS hostname is accepted as an image source. Likely intentional (CDN/S3 domains vary), but worth a second look if not — this is broader than most storefronts need.

---

## What's solid

- **Environment-gated Django settings** — `base.py`/`development.py`/`production.py` split cleanly; `DEBUG=False` forced in prod; `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` all required env vars with no insecure fallback (deploy fails loud if misconfigured, rather than silently running with dev-safe defaults).
- **Real security headers in production** — HSTS (1yr, includeSubDomains, preload), SSL redirect, secure session/CSRF cookies, `X_FRAME_OPTIONS: DENY`, content-type nosniff.
- **Sentry wired in** for error tracking, plus structured JSON logging to stdout in prod.
- **Payment gateways look genuinely implemented**, not stubbed — both Stripe and PayPal have real `capture`/`refund`/`cancel`/`retrieve` methods. Stripe webhook signatures are verified via `construct_webhook_event()` before processing (`gateways/stripe.py`).
- **No secrets committed** — confirmed via `git log --all --full-history` on `.env`/`.env.*`, and both are correctly gitignored.
- **Backend test coverage exists** — 31 test files across the Django apps (payments, orders, users, etc.).
- **Strict TypeScript** — `tsconfig.json` has `"strict": true`; no stray `console.log`/`console.debug` left in `frontend/src`.
- **No TODO/FIXME/HACK litter** — one false-positive match (a code comment containing the word "xxx" as a placeholder ID example), otherwise clean.

---

## Recommended order of operations

1. Wire up rate limiting on login/checkout/webhook endpoints (blocker #1) — highest risk, lowest effort.
2. Pin backend dependencies (blocker #2) — prevents a surprise breakage on the next deploy.
3. Add an idempotency key to Stripe payment intent creation (blocker #4) — prevents double-charge risk.
4. Stand up frontend tests for checkout + chat/WebSocket logic (blocker #3) — larger effort, but the highest-complexity client code has zero coverage right now.
5. Confirm CI actually runs lint/tsc/tests before merge (minor #5).
6. Revisit the wildcard image remote pattern if it wasn't intentional (minor #6).
