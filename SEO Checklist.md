# SEO Checklist - Next.js + Django/Postgres Ecommerce

## Domain / Hosting
- [ ] Identical content and URL structure if switching hosting platforms behind the same domain (no SEO impact if content/URLs match)
- [ ] Low TTL on DNS before any host migration to avoid crawl downtime
- [ ] Both platforms must have valid HTTPS certs before switching
- [ ] No error responses (500s, bad redirects) during host cutover

## Rendering Strategy (Next.js)
- [ ] Confirm rendering approach: SSR per request vs ISR
- [ ] Recommended: ISR with revalidation (e.g. `revalidate: 3600` or on-demand revalidation on product update) instead of full per-request SSR - same SEO benefit, better performance, lower DB load
- [ ] If staying SSR per request: cache Django API responses (Redis or Next.js fetch cache) so crawler traffic doesn't hit Postgres directly on every request
- [ ] Verify server-rendered HTML actually contains price/availability/description (not client-fetched post-hydration) using Search Console URL Inspection tool

## URL Structure
- [ ] Clean URLs: `/category/subcategory/product-name`, no query-string IDs
- [ ] Slugs via Django `SlugField`, not numeric IDs
- [ ] Canonical tags on filter/sort URLs pointing to base category URL (avoid infinite crawl paths and duplicate content)
- [ ] 301 redirects at Django level for any slug/URL changes

## Sitemap / Robots
- [ ] XML sitemap generated from Postgres (via `app/sitemap.ts` in Next.js App Router or a dedicated Django endpoint)
- [ ] Cache/regenerate sitemap periodically (e.g. every few hours), don't hit DB on every sitemap request
- [ ] robots.txt configured correctly
- [ ] Submit sitemap to Google Search Console after launch

## Metadata (per product/category)
- [ ] Unique title tag and meta description per product - no templated duplicates
- [ ] Meta title, meta description, canonical URL as explicit model fields in Django (not auto-generated only from templates)
- [ ] Generated dynamically in Next.js via metadata API / `next/head`, pulled from Django data

## Structured Data
- [ ] JSON-LD structured data (Product, Offer, AggregateRating) server-side rendered on product pages

## Content
- [ ] Original product descriptions - never copy manufacturer copy (duplicate content penalty)
- [ ] Unique descriptive content on category pages, not just product grids
- [ ] Alt text on all product images, pulled from product data
- [ ] Blog/guides section targeting informational searches (buying guides, comparisons, how-to) - usually the biggest early ranking driver for new ecommerce sites

## Images / Performance
- [ ] `next/image` for optimization
- [ ] Index Postgres queries used on product pages
- [ ] Monitor TTFB and Core Web Vitals (ranking factor)

## Error Handling
- [ ] Deleted/out-of-stock products return proper 404/410, not a soft-404 with 200 status

## Off-page / Authority
- [ ] Backlink outreach: suppliers, partners, PR, guest posts
- [ ] Google Business Profile if there's a local angle

## Pre-launch Setup
- [ ] Google Search Console installed
- [ ] Google Analytics/GA4 installed
- [ ] Google Merchant Center if pursuing Google Shopping listings
- [ ] Submit sitemap once live

## Expectations
- New domains typically take 3-6+ months to see organic traction
- Run paid ads or marketplace listings (Amazon, etc.) in parallel while SEO builds
