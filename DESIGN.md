# Axiom Storefront Design System

The storefront family shares a single Axiom frame mark, accessible commerce patterns, and image-first product discovery. Each vertical expresses that system through a different editorial world rather than a color swap.

## Shared shell

- Floating glass navigation: translucent storefront color, thin light border, soft shadow, strong backdrop blur.
- Axiom triangle mark: botanical leaf for Dispensary, molecular nodes for Peptides, resin strata for Hash.
- Body typography: Space Grotesk. Utility and measurement labels: IBM Plex Mono.
- Motion is restrained to slow hero-image drift and small interaction transforms, with reduced-motion support.
- Catalog photography remains the primary content in category and product cards; generated art is limited to atmosphere-setting hero imagery.

## Axiom Dispensary

- Tone: warm botanical field journal.
- Display type: Cormorant Garamond.
- Palette: forest `#172319`, amber `#c8792e`, parchment `#f8f3f0`.
- Layout: oversized editorial headline layered against macro flower photography, followed by mood-led discovery and the existing commerce sections.
- Shape language: soft capsules and rounded organic cards.

## Axiom Peptides

- Tone: precise specimen index.
- Display type: Geist; IBM Plex Mono is reserved for indices and research metadata.
- Palette: laboratory green `#071b17`, signal mint `#4cdca5`, cool paper `#f4f7f6`.
- Layout: rigid split hero, numbered reference labels, four-column compound-family plates, dense product index.
- Shape language: squared grids, fine rules, minimal radius.

## Axiom Hash

- Tone: cinematic collector archive.
- Display type: Six Caps for major headings, supported by Space Grotesk and IBM Plex Mono.
- Palette: near-black brown `#100c09`, resin gold `#d9962f`, bone `#f5f0e6`.
- Layout: full-bleed resin macro, condensed monumental headline, asymmetrical process plates, dark product room.
- Shape language: hard editorial frames with selectively rounded product cards.

## Responsive and performance rules

- Hero imagery uses responsive Next Image sizing and optimized WebP assets.
- Below-fold catalog imagery remains lazy-loaded; priority loading is limited to hero and first visible product rows.
- Mobile layouts preserve the same hierarchy without relying on hover and avoid horizontal overflow.
- All decorative motion must honor `prefers-reduced-motion`.

## Commerce admin

- The Django admin uses Unfold's neutral shell with a restrained purple operational accent.
- The landing dashboard prioritizes confirmed revenue, orders, purchasing customers, catalog health, order status, storefront performance, and recent activity from live database aggregates.
- Dashboard cards use compact 12px radii, fine gray borders, limited shadows, and dense tables suited to back-office work rather than storefront styling.
- Desktop admin surfaces use a 14px root scale (87.5% of the browser default) to match the reference's dense operational view; narrow touch layouts return to the standard 16px root scale.
- The wide revenue chart and supporting panels collapse into a single column below 1100px; KPI cards collapse from four to two, then one on phones.
- Empty states remain visible and informative when a new environment has no orders or storefront data.
- Product, category, and blog admin lists lead with 48px square image previews; missing media uses a quiet icon state without shifting row geometry.
