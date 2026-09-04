# HappyCana — Frontend Performance Audit

**Repo:** zicojojo/happycana
**Scope:** Frontend (Next.js/React) — unnecessary re-renders, redundant
fetches/waterfalls, memoization gaps, and general client-perf issues.
Companion to `backend_performance_audit.md`.

Static read-through, no profiler/Lighthouse run. Note: `next.config.ts` has
`reactCompiler: true` enabled, which auto-memoizes most component-level
render work — so classic "wrap this in `useMemo`/`useCallback`" advice is
largely moot here except where noted. The compiler does **not** change how
external store subscriptions (Zustand) decide to re-render, which is where
the real findings below live.

---

## Unnecessary re-renders

### 1. Zustand stores subscribed without a selector
`components/layout/navbar/Navbar.tsx:39`, `components/shop/CartDrawer.tsx:86`,
`app/account/addresses/page.tsx:42`

```ts
const { user, isAuthenticated, isGuest, logout } = useAuthStore()   // Navbar
const { isOpen, closeCart } = useCartStore()                        // CartDrawer
const { user, isAuthenticated, logout } = useAuthStore()             // addresses page
```

Calling the store hook with no selector subscribes the component to *every*
field in that store, not just the ones destructured. For `CartDrawer` this
means the drawer re-renders on every `cart` object update (every add/update/
remove-from-cart mutation, every 30s cart re-fetch) even when the drawer is
closed and only cares about `isOpen`/`closeCart`. `Navbar`'s three
auth fields happen to always change together (`setUser` sets all three at
once), so it's lower-impact there, but it's still a latent trap — any future
field added to `AuthState` re-renders `Navbar` on every change by default.

**Fix:**
```ts
const isOpen    = useCartStore(s => s.isOpen)
const closeCart = useCartStore(s => s.closeCart)
```
or a single selector with `useShallow` from `zustand/react/shallow` if
multiple fields are needed together.

### 2. `useCategoriesMenuTree` rebuilds the whole nav tree on every render
`hooks/useCategoriesMenuTree.ts:22-63`

No `useMemo` around the `categories.map(categoryToNode)` / `brands.map(...)`
/ `effects.map(...)` tree-building. `categories`/`brands`/`effects` are
stable object references from React Query between renders (unchanged data
→ same reference), so this work is redone for no reason on every render of
whatever calls the hook — which, per #1, includes every unrelated `Navbar`
re-render from the whole-store `useAuthStore()` subscription.

**Fix:** wrap the derived `rootNodes` (and intermediate nodes) in
`useMemo([categories, brands, effects])`. Low urgency on its own — the
category count is small — but it compounds with #1.

---

## Fetch/caching notes (not bugs, but worth flagging)

### 3. Duplicate `getProduct`/`getCollection` fetch relies on Next.js request memoization — FIXED
`app/shop/products/[slug]/page.tsx:30,102`, `app/shop/collections/[slug]/page.tsx:16,29`

Both `generateMetadata` and the page component call `getProduct(slug)` (or
`getCollection(slug)`) independently. This was only a single network request
because Next.js's automatic `fetch()` request memoization collapses
identical `url`+`options` calls within one render pass — and both call
sites used identical `timedFetch` args (`next: { revalidate: ... }`).
Correct as written, but fragile correctness-by-convention: if either call
site's fetch options ever drifted, the dedup would silently break and the
page would fetch the same resource twice server-side.

**Fix applied:** `getProduct` (`app/shop/products/[slug]/page.tsx`) and
`getCollection` (`lib/catalog.server.ts`) are now wrapped in React's
`cache()`, so the two call sites explicitly share one fetch per request
regardless of whether their options stay identical in the future.

---

## What's already handled well

- **Streaming/parallel data fetching** — `app/shop/page.tsx` splits every
  section (`CategoryGridSection`, `EffectsSection`, `BrandStripSection`,
  `OnDiscountSection`, `BestSellersSection`, `NewArrivalsSection`,
  `CollectionsSections`) into its own async Server Component wrapped in its
  own `<Suspense>` boundary — sections stream and resolve independently
  instead of one slow section blocking the whole page.
- **Parallelized prefetching** — `app/shop/products/page.tsx` and
  `app/shop/collections/[slug]/page.tsx` both use `Promise.all([...])` to
  fire `products`/`categories`/`brands`/`effects` prefetch queries
  concurrently rather than sequentially awaiting each one (`CollectionsSections`
  in `app/shop/page.tsx` does the same for per-collection product fetches).
- **Deliberate cache tuning** — `lib/catalog.server.ts` sets sane
  `revalidate` windows per endpoint (1h for mostly-static catalog data,
  `no-store`/`revalidate: false` for the effectively-unbounded filtered
  product grid) rather than one blanket policy.
- **React Query hygiene** — `hooks/useApi.ts` sets sensible `staleTime` per
  query, uses `enabled` guards to avoid firing cart/notification queries
  before auth is known, and `refetchOnMount: false` on the product grid
  specifically to avoid a hydration-mismatch refetch race — all with inline
  comments explaining why.
- **WebSocket lifecycle** — `hooks/useWebSocket.ts` and `hooks/useChat.ts`
  both correctly clean up sockets/timers on unmount, guard state updates
  with a `mountedRef`, and distinguish terminal close codes (4001/4003, no
  point retrying) from transient drops (exponential backoff up to 5
  retries). No leaks found.
- **Component memoization where it matters** — `ProductCard` and
  `CartLineItem` are wrapped in `memo()` for list contexts where they
  re-render at volume; combined with `reactCompiler: true`, most other
  components get this automatically.
- **Images** — no raw `<img>` tags anywhere in `src/`; everything goes
  through `next/image` with a custom imgix loader, explicit `sizes`, and
  `priority` only on above-the-fold cards.
- **`ProductsGrid`** — query params are read straight from the URL (no
  duplicate local state fighting the URL), search is debounced by design
  (only fires on Enter, not per keystroke), and pagination/filtering all
  flow through React Query's cache key rather than manual re-fetch logic.

---

## Recommended order of operations

1. ~~Fix #1 (`CartDrawer`/`Navbar`/addresses-page store selectors)~~ — done.
2. ~~Fix #2 (`useCategoriesMenuTree` memoization)~~ — done.
3. ~~Fix #3 (`getProduct`/`getCollection` explicit `cache()`)~~ — done.
