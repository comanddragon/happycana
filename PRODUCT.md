# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The storefronts serve both everyday retail shoppers who need quick, approachable product discovery and experienced enthusiasts or research buyers who expect category-specific detail, provenance, formats, and specifications.

## Product Purpose

A multi-store commerce platform presenting three isolated catalogs under one Axiom family: Axiom Dispensary, Axiom Peptides, and Axiom Hash. Success means visitors immediately recognize which storefront they are in, find relevant products through an attractive image-led experience, and complete shopping without data, branding, navigation, or cart state leaking across storefronts.

## Positioning

One commerce platform with genuinely distinct category expertise: cannabis retail, research peptide supply, and hash craft each receive their own product language and visual system while retaining a consistent underlying checkout and account experience.

## Operating Context

Visitors browse category and product imagery, compare variants and prices, inspect product-specific metadata, manage a cart, and check out. Storefront identity is resolved from isolated hostnames such as `dispensary.<domain>`, `peptides.<domain>`, and `hash.<domain>`.

## Capabilities and Constraints

- Next.js storefront backed by a shared Django commerce API and database.
- Storefront content and state must remain isolated by resolved storefront/hostname.
- Axiom Peptides must retain research-use-only language and avoid unsupported medical claims.
- Axiom Hash and Axiom Dispensary retain the existing age-gate and regulated-product messaging.
- Existing shopping, authentication, filtering, cart, checkout, and responsive behavior must continue working through the redesign.
- Real scraped or owned catalog images should lead the experience; fabricated product claims, reviews, test results, licensing details, and provenance are not permitted.

## Brand Commitments

- Preserve the Axiom family name.
- Use the names **Axiom Dispensary**, **Axiom Peptides**, and **Axiom Hash**.
- Rebuild all three logos as a coordinated family with distinct storefront marks.
- Give each storefront a clearly different layout, typography, and color system rather than recoloring one shared template.
- Make the storefronts image-first and more attractive to visitors.

## Evidence on Hand

- Real product and category photography is present in the catalog and scraper outputs.
- Storefront-specific product descriptions, categories, variants, prices, and availability are present in the database.
- Existing implementation documents the working commerce flows and domain isolation.
- No verified testimonials, performance claims, medical outcomes, or comparative benchmarks are available and none should be invented.

## Product Principles

- Storefront identity must be unmistakable within the first viewport.
- Product imagery and real catalog information earn attention and trust.
- Distinction must extend through composition, type, navigation, and interaction—not palette alone.
- Shared commerce behavior remains predictable even when each storefront’s presentation differs.
- Performance, accessibility, and mobile usability are part of visual quality.

## Accessibility & Inclusion

Maintain semantic navigation, keyboard operation, visible focus states, readable contrast, reduced-motion support, useful image alternatives, and responsive layouts across all storefronts.
