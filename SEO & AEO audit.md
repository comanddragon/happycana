Audit site for modern SEO and AEO with practical, prioritized recommendations

Last updated: 2026-09-01 — this revision re-verified every claim below directly against the codebase (models, serializers, views, admin, and every frontend route/component touched), corrected a few inaccuracies in the previous pass, and records what's been fixed vs. what's still open.

Overall assessment
HappyCana is a small e-commerce site (Next.js App Router, ~16 routes, server-rendered) for a licensed cannabis dispensary offering same-day pickup/delivery. The technical foundation is better than most sites this size: pages are server-rendered so content is crawlable without JS execution, per-page metadata is implemented correctly, the product detail page ships real Product JSON-LD, and a dynamic sitemap already covers the catalog. The age-gate is done right — it's a client-side overlay on top of content that's already in the server-rendered HTML, so it doesn't block crawlers.

The real gap isn't technical plumbing — it's content. The entire site is transactional (browse → verify age → buy) with almost no informational content. For a cannabis retailer this matters more than for a typical DTC brand, because Google Ads and Meta Ads both prohibit cannabis advertising — organic search and answer engines (Google AI Overviews, ChatGPT, Perplexity) are close to the only scalable, unpaid discovery channel available. Those channels overwhelmingly surface pages that directly answer specific questions ("how long do edibles take to kick in," "indica vs. sativa for sleep," "what does a COA show"), and this site has none of that — just a 6-item logistics FAQ and short conversion copy. That's the highest-leverage thing to fix, well above adding more schema or a robots.txt. **A blog + blog-detail page is planned next, which is exactly the vehicle for this — see "Blog, when it lands" below.**

A second, smaller theme: the site makes real trust claims (100% batch testing, third-party COAs, licensed retailer) but nothing backs them with crawlable, verifiable content — no COA archive, no license/location details, no way for a search engine or an AI answer engine to independently confirm any of it. For a regulated product, verifiable trust content is also a ranking and citation signal, not just UX copy.

────────────────────────────────────────
Backend SEO field audit (models + serializers)
────────────────────────────────────────

- `Product` — has `meta_title` (60 char) / `meta_description` (160 char), correct limits, exposed on the detail serializer (`ProductSerializer`) and used correctly by `generateMetadata` on the PDP.
- `Category` / `Brand` — **fixed this pass.** Neither had meta fields at all; both now have `meta_title`/`meta_description` (same 60/160 limits as Product), migrated, serialized, and editable in Django admin. Nothing on the frontend consumes them yet, since there's no dedicated category/brand landing page (see faceted-URL item below) — the fields exist and are ready for when there is one.
- `Effect` — still no meta fields. Lower priority: effects are used as filter chips (`?effect=slug`), not landing pages, today.
- `Lab.coa_url` / `coa_file` — real, per-variant data. **Correction to the previous audit:** this isn't just a badge graphic — `ProductDetails.tsx` already renders a real "View Certificate of Analysis" link whenever `lab.coa_url` is populated. The gap here is operational (are COAs actually being uploaded per batch?), not code. `Lab` also wasn't registered in Django admin at all before this pass — fixed, plus added as an inline on the variant admin page so it's actually editable.
- `Stock` (in the `inventory` app: `quantity`, `reserved`, `.available`) — real inventory tracking exists, and the backend already filters on it (`?in_stock=true` via `ProductFilter`/`ProductVariantFilter`). **Fixed this pass:** it was never exposed as a field on `ProductVariantSerializer`, so nothing (JSON-LD `availability`, UI badges) could reflect real stock. Both `ProductVariantSerializer` and `ProductVariantSummarySerializer` now expose a computed `in_stock` boolean, backed by the existing stock prefetch (`with_stock()`/`.full()`), with the product-list queryset updated to prefetch stock too so the grid doesn't take an N+1 hit for it.
- `Brand` — wasn't registered in Django admin at all before this pass (fixed alongside the meta fields), so even existing fields like `logo_url`/`website` had no admin UI.

Prioritized issues
1. No informational/answer content anywhere (highest priority) Outside of /help/faq (6 logistics Q&As) and short marketing blurbs on the homepage, there's zero educational content — no effect explainers, dosing guidance, indica/sativa/hybrid basics, terpene guides, or "how COA testing works" content. These are exactly the queries people put into Google and AI assistants before buying cannabis, and exactly the content answer engines like to cite. The EffectsStrip component (Uplift/Unwind/Rest/Focus/Social) and the LabTrust section already hint at the right topics but never develop them into real pages. **The planned blog is the right fix for this — see below.**

2. Trust/compliance claims aren't backed by verifiable content The homepage states "100% batches tested," "12 panel screen," and shows a COA badge graphic. As noted above, real COA data and rendering already exist at the product level — the gap is that `BatchGrid.tsx` on the homepage hardcodes fake "this week's batch" data (fabricated lot numbers, THC%, test dates) under the line "scan it to read the full certificate of analysis," which nothing backs. That's a content/trust liability specific to that component, not a site-wide missing feature. Still open — needs product/design decision on whether to pull real featured products+lab data in, not just a schema fix.

3. No canonical URLs on faceted shop pages — **fixed this pass.** `/shop/products` is filtered via query params (`?category=`, `?ordering=`, `?search=`, `?page=`) and previously had zero canonical anywhere in the codebase (confirmed by grep). `generateMetadata` on that route now sets `alternates.canonical` pointing every sorted/paged/searched variant back to the base category URL (or the unfiltered listing URL when there's no category), so ranking signals consolidate onto one URL per category instead of fragmenting across query-param variants. Also fixed: the raw `category` param was interpolated straight into the title/description/`<h1>` with no normalization (`category=flower` → "flower Products", lowercase); it's now title-cased via a small formatter (`flower` → "Flower Products").

4. Utility pages inherit indexable defaults — **fixed this pass.** `/login`, `/register`, `/shop/checkout`, and everything under `/account/*` had no page-level metadata export, so they inherited the root layout's `robots: { index: true, follow: true }`. All four are client components (`'use client'`), so metadata couldn't be added to the page files directly — fixed via sibling/nested server `layout.tsx` files that set `robots: { index: false, follow: false }` (for `/account/*`, this required splitting the existing client layout into a new server `layout.tsx` plus a client `AccountShell` component, since a `'use client'` file can't export `metadata`). **Still open:** `robots.ts` also has no explicit `disallow` rules for these paths (just a blanket `allow: '/'`) — noindex via metadata is the stronger signal since it removes existing indexed URLs, but adding `disallow` entries is still worth doing as a belt-and-suspenders fix. Deferred to the next pass.

5. FAQ content is good but not marked up, and it's the one schema addition actually worth doing The FAQ page has genuine, specific, non-generic Q&As (age verification, shipping windows, returns, state restrictions). This is one of the few places where adding FAQPage JSON-LD is worth the effort — the content already exists and fits the schema honestly, unlike bolting schema onto pages that don't have matching visible content. **Still open** — deferred to the next pass.

6. Local intent isn't addressed at all Copy references in-store pickup ("ready in about 20 minutes") and delivery "within our service area," implying a physical/local business, but there's no address, hours, or location data anywhere in the code, and no evidence of Google Business Profile integration. If there's a real storefront, "dispensary near me" / local-pack visibility is likely a bigger opportunity than most organic blue-link SEO for this business — worth confirming outside the codebase (Google Business Profile setup isn't a code change) rather than assuming from what's here. Still open.

7. Product JSON-LD was inaccurate — **fixed this pass.** The PDP's `Product` schema previously hardcoded `availability: InStock` unconditionally (now driven by the real `in_stock` field from the backend, per variant, defaulting to `OutOfStock` when no variant is in stock), always used `base_price` even when variants price differently (now emits an `AggregateOffer` with `lowPrice`/`highPrice`/`offerCount` when variant prices differ, or a single `Offer` with the real variant `sku` otherwise), and was missing `url`/`sku` entirely (now both present). A `BreadcrumbList` block (Shop → Category → Product) was also added — there wasn't one anywhere on the site before. PDP metadata also gained `alternates.canonical` and Twitter Card tags, neither of which existed before.

8. Minor gaps, still open: no Twitter Card metadata on any page other than the PDP (root layout and other routes still lack it); no default OG image at the root level — **correction to the previous audit:** it's not just the homepage that falls back to nothing, `/shop` also only sets OG title/description text with no image, so the *only* page that ever sets an OG image is the PDP, and only when `product.primary_image` exists; three real empty `alt=""` attributes remain on actual product thumbnails (`components/checkout/OrderSummary.tsx:51`, `components/shop/ProductDetails.tsx:141`, `app/account/orders/[id]/page.tsx:106` — note `CategoryGrid.tsx`'s empty alt is fine as-is, the category name is already visible text directly below that image, so it's correctly decorative); no analytics or Search Console verification found, so none of this can currently be measured. All deferred to the next pass.

What's already fine — don't touch
Server-side rendering / metadata / JSON-LD generation (crawlers see fully-rendered content, no client-side-only content risk).
Heading structure (single h1 per page, sensible h2 sectioning).
The dynamic sitemap and the age-gate implementation — the age-gate handles the tricky part correctly (client-side overlay over already-server-rendered HTML). **Correction:** the sitemap is not fully fine — see "still open" below, it's missing several static routes and caps at 1000 products with no pagination.
robots.txt — **correction to the previous audit, which said this file was missing.** `app/robots.ts` exists and generates a valid robots.txt with `allow: '/'` and a `sitemap` pointer. It just doesn't yet disallow the utility paths noted in item 4 — see "still open."

────────────────────────────────────────
Fixed this pass (backend + frontend)
────────────────────────────────────────
- Backend: `Category`/`Brand` gained `meta_title`/`meta_description` fields (migrated, serialized, admin-editable).
- Backend: `Brand` and `Lab` registered in Django admin (previously missing entirely); `Lab` added as an inline on the variant admin.
- Backend: `ProductVariantSerializer` / `ProductVariantSummarySerializer` now expose a real `in_stock` boolean backed by the existing `Stock` model; product-list queryset updated to prefetch stock so this doesn't add an N+1.
- Frontend: PDP (`/shop/products/[slug]`) — added `alternates.canonical`, Twitter Card metadata, accurate JSON-LD `availability`/`AggregateOffer`/`sku`/`url`, and a new `BreadcrumbList` block.
- Frontend: `/shop/products` (faceted listing) — added `alternates.canonical`, fixed raw-param title/H1 casing.
- Frontend: `/login`, `/register`, `/shop/checkout`, `/account/*` — all noindexed via new/split server layouts.
- Frontend: `types/index.ts` updated to match the new backend fields (`Category`/`Brand` meta fields, `ProductVariant.in_stock`).
- All changed frontend files pass `tsc --noEmit` and `eslint` with zero errors.

────────────────────────────────────────
Still open — next pass
────────────────────────────────────────
1. Add `FAQPage` JSON-LD to `/help/faq` using the existing question/answer copy — no new content needed, direct AEO win.
2. Add `disallow` rules to `robots.ts` for `/login`, `/register`, `/shop/checkout`, `/account/*` (belt-and-suspenders alongside the noindex metadata already shipped).
3. Root layout: add default Twitter Card metadata and a default OG image so pages other than the PDP don't fall back to nothing when shared on social; consider an OG image for `/shop` specifically given it's the highest-traffic non-PDP page.
4. Sitemap: add `/shop/products`, `/help/faq`, `/terms`, `/privacy`, and category URLs; fix the `page_size=1000` cap on the products fetch (currently silently drops anything past that with no pagination).
5. Fix the 3 remaining empty `alt=""` attributes on real product thumbnails (listed above).
6. Build out 4-6 real answer-style content pages tied to the effects/categories already modeled in the backend (e.g., "Indica vs. Sativa vs. Hybrid," "How Long Do Edibles Take to Kick In," "What's on a Cannabis COA and Why It Matters," "Terpenes 101"). Link them from EffectsStrip and product pages where relevant.
7. Decide what to do about `BatchGrid.tsx`'s hardcoded fake batch data — either wire it to real featured products + lab data, or soften the copy so it isn't presented as verifiable.
8. Confirm whether there's a physical storefront and, if so, get a Google Business Profile in place and add address/hours/`LocalBusiness` details to the site.
9. Add analytics + Search Console verification — nothing here is measurable without this.

────────────────────────────────────────
Blog, when it lands
────────────────────────────────────────
A blog index + blog detail page are planned next. Points to build in from day one rather than retrofit later:
- **This is the actual fix for issue #1 above** (no answer/informational content) — treat post topics as directly answering the specific questions people ask Google/AI assistants before buying cannabis (dosing, indica/sativa/hybrid, terpenes, COA literacy), not generic brand-blog content.
- Backend: will need its own model with the same meta-field pattern already established on `Product`/`Category`/`Brand` (`meta_title` 60 char, `meta_description` 160 char) plus a canonical `slug`, published/draft state, and a real publish timestamp for `Article` JSON-LD's `datePublished`/`dateModified`.
- Frontend: blog index and detail pages should follow the same pattern just built for the PDP — `alternates.canonical`, Twitter Card + OG image metadata, and `Article`/`BlogPosting` JSON-LD (with `author`, `datePublished`, `image`) from day one rather than retrofitted later.
- Add both the blog index and every published post to the sitemap fix in item 4 above — build that generically enough (e.g. a paginated fetch instead of the current single `page_size=1000` call) that adding a second content type doesn't repeat the same capping bug.
- Internal-link posts from the relevant `EffectsStrip` entries, category pages, and PDPs (e.g. a "Terpenes 101" post linked from every product's terpene profile section) — this is what actually turns the content into a ranking/citation asset instead of an isolated blog nobody finds.
- FAQPage-style schema doesn't apply to posts; use `BlogPosting` (or `Article`) instead, and only add `FAQPage` markup on a post if it's genuinely structured as Q&A.
