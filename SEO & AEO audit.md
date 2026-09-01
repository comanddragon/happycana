Audit site for modern SEO and AEO with practical, prioritized recommendations

Status update (2026-09-01): Recommended next steps 1-5 below have been implemented — see "Shipped" notes inline and the summary at the bottom. A follow-up pass has also shipped part of step 6 (per-product COA links were already wired up; the homepage's fabricated batch/lot data has now been replaced with real product data) and part of step 8 (Twitter Card, default OG image, and the remaining empty alt="" attributes). Still open: a dedicated Lab Results index page, Google Business Profile / local business details, and a static robots.txt (a dynamic app/robots.ts already covers this, so it's not urgent).

Overall assessment
HappyCana is a small e-commerce site (Next.js App Router, ~16 routes, server-rendered) for a licensed cannabis dispensary offering same-day pickup/delivery. The technical foundation is better than most sites this size: pages are server-rendered so content is crawlable without JS execution, per-page metadata is implemented correctly, the product detail page ships real Product JSON-LD, and a dynamic sitemap already covers the catalog. The age-gate is done right — it's a client-side overlay on top of content that's already in the server-rendered HTML, so it doesn't block crawlers.

The real gap isn't technical plumbing — it's content. The entire site is transactional (browse → verify age → buy) with almost no informational content. For a cannabis retailer this matters more than for a typical DTC brand, because Google Ads and Meta Ads both prohibit cannabis advertising — organic search and answer engines (Google AI Overviews, ChatGPT, Perplexity) are close to the only scalable, unpaid discovery channel available. Those channels overwhelmingly surface pages that directly answer specific questions ("how long do edibles take to kick in," "indica vs. sativa for sleep," "what does a COA show"), and this site has none of that — just a 6-item logistics FAQ and short conversion copy. That's the highest-leverage thing to fix, well above adding more schema or a robots.txt.

A second, smaller theme: the site makes real trust claims (100% batch testing, third-party COAs, licensed retailer) but nothing backs them with crawlable, verifiable content — no COA archive, no license/location details, no way for a search engine or an AI answer engine to independently confirm any of it. For a regulated product, verifiable trust content is also a ranking and citation signal, not just UX copy.

Prioritized issues

1. No informational/answer content anywhere (highest priority) — ✅ Shipped
Outside of /help/faq (6 logistics Q&As) and short marketing blurbs on the homepage, there's zero educational content — no effect explainers, dosing guidance, indica/sativa/hybrid basics, terpene guides, or "how COA testing works" content. These are exactly the queries people put into Google and AI assistants before buying cannabis, and exactly the content answer engines like to cite. The EffectsStrip component (Uplift/Unwind/Rest/Focus/Social) and the LabTrust section already hint at the right topics but never develop them into real pages.
Shipped: 5 answer-style pages under /learn (Indica vs. Sativa vs. Hybrid, How Long Do Edibles Take to Kick In, What's on a Cannabis COA and Why It Matters, Terpenes 101, A Beginner's Guide to Cannabis Dosing) plus a /learn index. Each ships Article JSON-LD, is registered in the sitemap, and cross-links to the others and back to /shop/products. Linked from primary nav, the footer, and a new line under EffectsStrip on the homepage.

2. Trust/compliance claims aren't backed by verifiable content — partially shipped
The homepage states "100% batches tested," "12 panel screen," and shows a COA badge graphic. Per-product COA linking was already wired up on the PDP (ProductSpecs renders a "View Certificate of Analysis" link straight from the real lab.coa_url field whenever one is on file — this was already in the codebase, just not mentioned in the original pass of this audit). What was still a real problem: BatchGrid.tsx (the homepage's "this week's batch" section) and the floating jar in Hero.tsx both hardcoded fake product names, THC percentages, lot numbers, and test dates that had no relationship to the actual catalog — exactly the kind of unverifiable trust claim this audit flags. That's now fixed: both pull real, recently-added products from the catalog (via a shared lib/jarProduct.ts mapper), show their actual THC/terpene/effect data, link to the real product page, and surface a "Certificate of analysis available" indicator instead of a fabricated lot/test-date line.
Still open: there's no license-number detail page and no standalone "Lab Results" index page listing every batch's COA in one place (see step 6 below) — the per-product link is real, but there's no single crawlable page that aggregates all of them.

3. No canonical URLs on faceted shop pages — ✅ Shipped
/shop/products is filtered entirely via query params (?category=, ?ordering=, ?search=, ?page=) and there is no canonical anywhere in the codebase (confirmed by grep). generateMetadata on that route also folds the raw category param into the title/description with no normalization (e.g., a category=flower link produces "flower Products," lowercase and inconsistent). Combined with no canonical tag, this is the classic faceted-navigation problem: many crawlable URL variants for what's substantially the same content, diluting relevance signals instead of consolidating them onto one strong "Flower" page.
Shipped: generateMetadata now sets alternates.canonical to the base listing (/shop/products, or /shop/products?category=X when a category is set), consolidating every sort/search/page/brand/effect/etc. combination onto one URL per category. Category name in both the <title> and the visible <h1> is now looked up against the real category list (falls back to a humanized slug) instead of rendering the raw lowercase slug.

4. Utility pages inherit indexable defaults — ✅ Shipped
/login, /register, and everything under /account/* have no page-level metadata export, so they inherit the root layout's robots: { index: true, follow: true } and the generic site title/description. These pages have no unique content and shouldn't be indexed — low risk on a site this size, but a quick, safe fix.
Shipped: /login and /register each got a server-component layout.tsx exporting robots: { index: false, follow: false } (their page.tsx files are client components, so metadata has to live in a sibling layout). /account/layout.tsx was split into a server layout (exports the same noindex metadata) plus AccountLayoutClient.tsx, which carries all the existing client-side nav/UI unchanged.

5. FAQ content is good but not marked up — ✅ Shipped
The FAQ page has genuine, specific, non-generic Q&As (age verification, shipping windows, returns, state restrictions). This is one of the few places where adding FAQPage JSON-LD is worth the effort — the content already exists and fits the schema honestly, unlike bolting schema onto pages that don't have matching visible content.
Shipped: FAQPage JSON-LD added to /help/faq, generated directly from the existing DEFAULT_FAQS array (in components/support/Faq.tsx) so the structured data can't drift out of sync with the visible Q&As.

6. Local intent isn't addressed at all — still open
Copy references in-store pickup ("ready in about 20 minutes") and delivery "within our service area," implying a physical/local business, but there's no address, hours, or location data anywhere in the code, and no evidence of Google Business Profile integration. If there's a real storefront, "dispensary near me" / local-pack visibility is likely a bigger opportunity than most organic blue-link SEO for this business — worth confirming outside the codebase (Google Business Profile setup isn't a code change) rather than assuming from what's here.

7. Minor gaps — mostly shipped
Partially shipped: analytics and Search Console verification are no longer absent — see the "Shipped" note under step 1 of Recommended next steps below.
Shipped: default Twitter Card metadata and a root-level default OG image (frontend/public/og-default.png, generated from the existing brand lockup) added to the root layout, so pages that don't set their own (homepage, /help/faq, /learn, etc.) now inherit a real social preview instead of falling back to nothing. The empty alt="" attributes on real product images (cart line items in OrderSummary, PDP thumbnails, order history, and category tiles) now carry the actual product/category name.

What's already fine — don't touch
Server-side rendering / metadata / JSON-LD generation (crawlers see fully-rendered content, no client-side-only content risk).
Heading structure (single h1 per page, sensible h2 sectioning).
The dynamic sitemap and the age-gate implementation — both already handle the tricky parts correctly (the sitemap now also lists /learn and its guide pages, see below).
robots.txt is missing but not urgent: the sitemap already declares priorities, and there's no evidence of anything on this small site that needs to be blocked from crawling (account/auth pages are now noindexed via metadata instead, see #4).

Recommended next steps, in order

1. Add analytics + Search Console verification. Nothing else here is measurable without this, and it's currently absent. — ✅ Shipped
A gated GA4 loader (components/providers/Analytics.tsx) was added to the root layout; it renders nothing unless NEXT_PUBLIC_GA_MEASUREMENT_ID is set, so it's a safe no-op until that env var is configured in each deployment. metadata.verification.google / msvalidate.01 were added to app/layout.tsx, reading from NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION and NEXT_PUBLIC_BING_SITE_VERIFICATION. Action needed from the team: set these three env vars in the deployment (Cloudflare/Vercel) once real GA4 and Search Console properties exist — nothing renders until they're set.

2. Add noindex, nofollow to /login, /register, and /account/* via a metadata export (or a shared layout-level metadata default) — quick, low-risk. — ✅ Shipped (see issue #4 above).

3. Add FAQPage JSON-LD to /help/faq using the existing question/answer copy — no new content needed, direct AEO win. — ✅ Shipped (see issue #5 above).

4. Normalize the faceted shop URLs: add alternates.canonical pointing filtered/sorted variants back to their base category or listing URL, and fix the category title casing in generateMetadata. — ✅ Shipped (see issue #3 above).

5. Build out 4-6 real answer-style content pages tied to the effects/categories already modeled in the backend (e.g., "Indica vs. Sativa vs. Hybrid," "How Long Do Edibles Take to Kick In," "What's on a Cannabis COA and Why It Matters," "Terpenes 101"). Link them from EffectsStrip and product pages where relevant — this is the biggest lever given the paid-ads restriction on this vertical. — ✅ Shipped (see issue #1 above). The product-detail-page linking follow-up is also done: lib/guides.ts now exports getGuideForProduct(), which maps a product's compliance_category/cannabis_type/lab data to the single most relevant guide (edibles → onset-time guide, any indica/sativa/hybrid product → the basics guide, otherwise COA or dosing as fallbacks), and ProductDetails.tsx renders that link right under the specs panel.

6. Make the lab-testing claims verifiable: link each product's real COA (even a simple PDF/image per batch) instead of only a badge graphic, and consider a small "Lab Results" index page. — partially shipped, see issue #2. Per-product COA linking already existed; the homepage's fabricated batch data has now been replaced with real product data. Still open: a standalone Lab Results index page aggregating every batch's COA.

7. Confirm whether there's a physical storefront and, if so, get a Google Business Profile in place and add address/hours/LocalBusiness details to the site — likely higher-impact for a dispensary than further organic content work, but it's a business/ops question, not just a code change. — still open, see issue #6.

8. Lower priority: add Twitter Card + a root-level default OG image, fix the empty alt="" attributes on real product images, add a static robots.txt once account pages are excluded. — ✅ Shipped (Twitter Card, OG image, alt text — see issue #7). Static robots.txt still not added — account pages are already excluded via noindex metadata and a dynamic app/robots.ts already exists, so this remains a "could do anytime, not urgent" item, not a blocker.

Summary of what shipped in this pass
- frontend/src/app/layout.tsx — GA4 loader + Search Console/Bing verification metadata (env-gated); default Twitter Card + root OG image metadata
- frontend/public/og-default.png — new, default 1200x630 social share image generated from the existing brand lockup
- frontend/src/components/providers/Analytics.tsx — new, gated GA4 script loader
- frontend/src/app/login/layout.tsx, frontend/src/app/register/layout.tsx — new, noindex metadata
- frontend/src/app/account/layout.tsx — now a server component exporting noindex metadata
- frontend/src/app/account/AccountLayoutClient.tsx — new, the account nav/shell client UI moved here unchanged
- frontend/src/app/help/faq/page.tsx — FAQPage JSON-LD from DEFAULT_FAQS
- frontend/src/app/shop/products/page.tsx — alternates.canonical + real category names in title/h1
- frontend/src/lib/guides.ts — shared registry of /learn guides + getGuideForProduct() mapping products to their most relevant guide
- frontend/src/components/learn/GuideArticle.tsx — new, shared article shell + Article JSON-LD for guide pages
- frontend/src/app/learn/page.tsx — new, guides index
- frontend/src/app/learn/indica-vs-sativa-vs-hybrid/page.tsx — new
- frontend/src/app/learn/how-long-do-edibles-take-to-kick-in/page.tsx — new
- frontend/src/app/learn/what-is-a-cannabis-coa/page.tsx — new
- frontend/src/app/learn/terpenes-101/page.tsx — new
- frontend/src/app/learn/beginners-guide-to-cannabis-dosing/page.tsx — new
- frontend/src/app/sitemap.ts — added /learn + guide URLs, /shop/products, /help/faq
- frontend/src/components/layout/navbar/constants.ts — added "Learn" nav link
- frontend/src/components/layout/Footer.tsx — added "Learn" footer column
- frontend/src/components/home/EffectsStrip.tsx — added a link into /learn
- frontend/src/components/shop/ProductDetails.tsx — links to the most relevant /learn guide under the specs panel; fixed empty alt="" on the media thumbnail strip
- frontend/src/lib/jarProduct.ts — new, maps a real Product to the homepage JarCard shape
- frontend/src/components/home/BatchGrid.tsx — now pulls real recently-added products instead of hardcoded placeholder batch data
- frontend/src/components/home/Hero.tsx — floating jar now shows a real product instead of hardcoded placeholder data
- frontend/src/components/home/JarCard.tsx — now links to the real product page and shows SKU/COA availability instead of a fabricated lot number and test date
- frontend/src/components/checkout/OrderSummary.tsx, frontend/src/app/account/orders/[id]/page.tsx, frontend/src/components/shop/CategoryGrid.tsx — fixed empty alt="" attributes on real product/category images
