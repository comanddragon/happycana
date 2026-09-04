# HappyCana — Backend Performance Audit

**Repo:** zicojojo/happycana
**Scope:** Backend (Django) — N+1 queries, missing indexes, unnecessary model
instantiation, repeated auth work, serializer size.

This is a static, read-through audit (no live DB/profiler run). Findings are
ordered by expected impact.

---

## N+1 queries

### 1. `ChatRoomSerializer.get_latest_message` / `get_unread_count`
`apps/chat/api/serializers.py:51-61`

`ChatRoomViewSet.get_queryset()` prefetches `"messages"`, but both methods
bypass that cache: `obj.messages.last()` and
`obj.messages.filter(...).exclude(...).count()` each issue a fresh query per
row (`.last()`/`.filter()` never use the `prefetch_related` cache). Every
room-list request costs 2N extra queries, and the `"messages"` prefetch
itself is dead weight since `ChatRoomSerializer` never renders a `messages`
field directly.

**Fix:** replace the blanket `"messages"` prefetch with two targeted
`Prefetch` objects using `to_attr` — one ordered `-created_at` (take `[0]`
for latest), one filtered `is_read=False` (filter out
`sender_id == request.user.id` in Python) — built per-request in
`get_queryset` since the exclusion depends on `request.user`.

### 2. Cart write endpoints missing the prefetch `CartView.get` has
`apps/orders/api/views.py`

`CartItemAddView.post`, `CartItemUpdateView.patch`, and
`CartItemUpdateView.delete` all fetch `cart` with no prefetch
(`Cart.objects.get_or_create(...)` / `Cart.objects.get(...)`), then serialize
it with `CartSerializer`. `CartItemSerializer.variant` is a full
`ProductVariantSerializer`, which touches `attributes`, `images`, `videos`,
`product`, `lab`, `stock_levels` — none of that is cached, so every
add/update/remove-from-cart call N+1s across 6 relations per cart item. Only
`CartView.get` prefetches (and even that's incomplete — see #3).

**Fix:** extract the queryset from `CartView.get` into a shared helper and
reuse it in all three views.

### 3. That prefetch is itself incomplete
`CartView.get`, `apps/orders/api/views.py:17-23`

`prefetch_related("items__variant__attributes")` only covers `attributes`.
`ProductVariantSerializer` also needs `images`, `videos` (prefetch),
`product`, `lab` (select_related — `lab` is a reverse O2O so
`select_related` works), and `stock_levels` (prefetch, for `get_in_stock`).
Five of six relations are missing.

**Fix:**
```python
Prefetch("items", queryset=CartItem.objects.select_related(
    "variant__product", "variant__lab"
).prefetch_related(
    "variant__attributes", "variant__images",
    "variant__videos", "variant__stock_levels",
))
```

### 4. Same gap on `OrderListView` / `OrderDetailView`
`apps/orders/api/views.py:56-74`

`prefetch_related("items__variant")` avoids re-fetching the variant FK
itself but still N+1s on `attributes`, `images`, `videos`, `lab`,
`stock_levels` inside `OrderItemSerializer.variant` (also
`ProductVariantSerializer`). Same fix pattern as #3, via a
`Prefetch("items", queryset=OrderItem.objects.select_related(...).prefetch_related(...))`.

---

## Unnecessary query / dead prefetch

### 5. `CheckoutService._get_cart`
`services/checkout.py:142-149`

Prefetches `"items__variant__stock_levels__warehouse"`, but the very next
line in `create_order` re-fetches items as
`cart.items.select_related("variant").all()` — a new queryset that ignores
the prefetch cache — and `_reserve_stock` correctly re-queries stock fresh
anyway (for the `select_for_update` lock, per the existing code comment). So
the prefetch runs, costs a query, and its result is never read.

**Fix:** drop the prefetch in `_get_cart`; it buys nothing given how
`create_order` actually consumes `cart`.

---

## Missing indexes

### 6. `Order.status`
`apps/orders/models.py` — no `Meta.indexes`

`OrderListView` filters admin queries by `status`
(`filterset_fields = ["status"]`) with no scoping to a single user for
staff — a full-table scan on an unindexed column as order volume grows.

**Fix:** `models.Index(fields=["status", "-created_at"])` (covers the admin
filter+ordering combo directly — generate via `makemigrations`).

### 7. `Product.is_active` + ordering
`apps/catalog/models.py`

`Product.objects.active()` (`is_active=True`) is the base of every
storefront listing, always combined with `Meta.ordering = ["-created_at"]`.
No composite index backs that filter+sort.

**Fix:** `models.Index(fields=["is_active", "-created_at"])` on `Product`.

### 8. `Notification` — `user` + `is_read` + ordering
`apps/notifications/models.py`

`NotificationListView` filters `user=` (+ optional `is_read=False`),
ordered by `-created_at` (`Meta.ordering`). FK on `user` is auto-indexed but
not composite with `is_read`/`created_at`.

**Fix:** `models.Index(fields=["user", "is_read", "-created_at"])`.

---

## What's already handled well

- `apps/catalog` — `ProductListView`, `ProductDetailView`,
  `CategoryManager.attach_full_tree` (explicitly solves an N+1 in the
  recursive category serializer), `LabResultListView` all have deliberate,
  correctly-scoped `select_related`/`prefetch_related`, with inline comments
  explaining why.
- `apps/blog` — list view `.defer("content_html", "content_text")` to avoid
  pulling large blobs on every row.
- `apps/shipping` — `Shipment` views consistently `select_related` +
  `prefetch_related("events")`.
- `services/checkout.py` — deliberately *not* prefetching stock before
  `select_for_update()`, with a comment explaining why a prefetched snapshot
  would be stale. Correct, not a bug (see #5 for the separate dead-prefetch
  issue on the cart fetch itself).
- No repeated-auth-work or unnecessary model instantiation found in
  `core/permissions.py` or `core/middleware.py` — permission checks are
  cheap attribute reads, no extra queries per check.
- No oversized serializers found beyond the `ProductVariantSerializer`-in-
  cart/order case above (#2-4) — the codebase already has lean/full
  serializer pairs (`ProductListSerializer` vs `ProductSerializer`,
  `ProductVariantSummarySerializer` vs `ProductVariantSerializer`) for that
  exact reason.

---

## Recommended order of operations

1. Fix #1 (chat room list) — hit on every poll/reload, 2N queries.
2. Fix #2/#3 (cart mutations) — hit on every add/update/remove-from-cart click.
3. Fix #4 (order list/detail) — same pattern, lower traffic than cart.
4. Fix #5 (dead prefetch in checkout) — free win, one line removed.
5. Add indexes #6-8 — cheap, compounding as tables grow.
