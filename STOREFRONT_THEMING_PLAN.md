# Storefront Theming & Isolation Plan

Scope: give the Dispensary and Peptides storefronts distinct visual identities
(color, type, radius, motif) without a component rewrite. Hash and Footwear
stay stubs (kind already exists in `StorefrontKind` and `FEATURES`, no UI
built) but the architecture below is designed so most of adding them later
is a config addition, not a refactor — see Section 7 for exactly what's
reusable and what still requires bespoke work each time.

Decisions locked in:
- Identity source: code config keyed by storefront `kind` (same pattern as
  `storefront/config.ts` FEATURES), not DB `branding` JSON. Changing a
  storefront's look means a code change + deploy, not an admin edit.
- Round 1 scope: Dispensary + Peptides only.
- Divergence depth: token-level (colors/fonts/radius) everywhere, plus
  targeted structural/content divergence on the specific components called
  out in Tier 3 below.

---

## 1. Current state (what's actually happening today)

- `src/app/layout.tsx` loads three Google fonts (Fraunces, Space Grotesk, IBM
  Plex Mono) unconditionally and assigns them to `--font-hc-display`,
  `--font-hc-body`, `--font-hc-mono` in `globals.css`. Every storefront gets
  the same three fonts. There is no font variation today, including on
  Peptides.
- `globals.css` defines a single static `@theme` block:
  `--color-hc-canopy`, `-canopy-2`, `-canopy-3`, `-amber`, `-amber-light`,
  `-amber-dim`, `-sage`, `-sage-dim`, `-paper`, `-paper-2`, `-ink`,
  `-ink-soft`. These compile to Tailwind utilities (`bg-hc-canopy`,
  `text-hc-amber-dim`, etc.) used across **64 files**: Navbar, Footer,
  CartDrawer, ProductCard, ProductDetails, every checkout step, blog, FAQ,
  login/register, lab-results, terms, privacy, the whole `home/*` section
  library.
- `<html>` already carries `data-vertical={storefront.kind}` — set, but
  nothing reads it. This is the hook the whole plan uses.
- Only two things branch by storefront kind today:
  1. `src/app/page.tsx` — renders `PeptideHome` instead of the dispensary
     home sections.
  2. Content-level splits that already exist and work correctly: `FEATURES`
     flags (`ageGate`, `cannabisCatalog`, `peptideCatalog`, `labResults`),
     `PEPTIDE_NAV_LINKS` vs `NAV_LINKS`, `PEPTIDE_COLUMNS` vs
     `CANNABIS_COLUMNS` in `Footer.tsx`, the two disclaimer paragraphs in
     `Footer.tsx`, and the `CannabisBadges`/`CannabisEffects`/
     `CannabisProductSpecs`/`CannabisBlogLink` components gated behind
     `features.cannabisCatalog` in `ProductDetails.tsx`.
- Everything else is one shared, dispensary-colored UI. `PeptideHome.tsx` is
  the only place that looks different, and it does so by hand: every color
  in that file is a raw hex literal (`#071b17`, `#9ee8ce`, `#19382f`, ...)
  disconnected from the token system, plus a one-off logo fallback in
  `Logo.tsx` (hardcoded `#9ee8ce`, hardcoded "A" initial) that isn't reused
  anywhere else and isn't parameterized per kind.
- Gap on the product detail page: `ProductDetails.tsx` shows
  `CannabisProductSpecs` (THC/CBD/terpenes/COA) for cannabis products but has
  **no equivalent for peptides** — no purity/concentration/COA block, no
  research-blog link. Peptide product pages are functionally blank where
  cannabis product pages are rich.
- Motif-level styling that bypasses tokens entirely (raw hex/shadow/rotate,
  won't respond to a CSS-variable override): `ProductCard.tsx` and
  `home/JarCard.tsx` share an identical "jar card" motif — `rounded-[22px]`,
  `from-[#fbf7ee]`, `shadow-[...rgba(23,20,15,...)]`,
  `hover:rotate-[-0.6deg]`. This organic/boutique motif reads as dispensary
  regardless of what colors sit under it, and it's the card peptides
  products render in today.

Net effect: "Peptides leaching off the dispensary storefront" is accurate.
One page (`/`) is bespoke; the navbar, footer, product grid, product page,
checkout, blog, and every legal page are the same dispensary-branded HTML
for both storefronts.

---

## 2. Architecture: theme tokens via CSS variable override

Tailwind v4's `@theme` block (already in use) emits real CSS custom
properties at `:root`. Every `bg-hc-canopy` / `text-hc-amber-dim` / etc.
utility compiles to `background-color: var(--color-hc-canopy)`. That means a
later, more specific CSS rule can redefine `--color-hc-canopy` and every
utility using it repaints, with zero component edits. This is exactly the
mechanism already used for dark mode (`.dark { --background: ...; }`) in the
same file — same pattern, scoped to `[data-vertical]` instead of `.dark`.

### 2.1 Token contract (`src/storefront/theme.ts`, new file)

A single typed config, one entry per `StorefrontKind`, that is the source of
truth for both the CSS override block and the font className logic in
`layout.tsx`. Shape:

```ts
export interface StorefrontTheme {
    colors: {
        canopy: string; canopy2: string; canopy3: string
        amber: string; amberLight: string; amberDim: string
        sage: string; sageDim: string
        paper: string; paper2: string
        ink: string; inkSoft: string
    }
    radius: string          // shadcn --radius equivalent, drives card/button roundness
    fonts: { display: 'fraunces' | 'peptideDisplay'; body: 'spaceGrotesk'; mono: 'ibmPlexMono' }
    productCardVariant: 'organic' | 'clinical'   // see Tier 3
}
```

Existing hex values become the `dispensary` entry verbatim (no visual change
for that storefront). A `peptides` entry is built from the palette already
proven out in `PeptideHome.tsx` (`#071b17` canopy, `#9ee8ce` amber-equivalent
accent, `#f4f7f6` paper, `#10231e` ink), so the homepage's existing design
becomes the site-wide peptide theme instead of a one-off.

`hash` and `footwear` entries can alias `dispensary` for now (literally
`FEATURES.hash` already aliases `dispensary` behavior) — adding a real theme
for them later is one object in this file, nothing else changes.

### 2.2 CSS override block (`globals.css`)

After the existing static `@theme` block (which stays as the dispensary
default — zero risk to the current site), add attribute-scoped overrides:

```css
html[data-vertical="peptides"] {
    --color-hc-canopy: #071b17;
    --color-hc-canopy-2: #05120f;
    --color-hc-amber: #4cdca5;
    --color-hc-amber-light: #9ee8ce;
    --color-hc-amber-dim: #197052;
    --color-hc-sage: #b9cec7;
    --color-hc-paper: #f4f7f6;
    --color-hc-paper-2: #dff3eb;
    --color-hc-ink: #10231e;
    --color-hc-ink-soft: #526a62;
    --font-hc-display: var(--font-peptide-display), sans-serif;
    --radius: 0.375rem;
}
```

Generated from the `theme.ts` values above (a tiny script or just kept in
sync by hand since there are only 2 entries right now — not worth codegen
for 2 rows). This one block reskins Navbar, Footer, CartDrawer, checkout,
blog, FAQ, legal pages, and the `AMBER_DOT`/`AMBER_BUTTON` inline gradients
in `navbar/constants.ts` (they already reference `var(--color-hc-amber...)`,
so they inherit automatically) — no edits needed to any of those files.

Rationale for keeping the `hc-canopy`/`hc-amber` variable *names*: renaming
~64 files' worth of class references to neutral names (e.g. `hc-surface`,
`hc-accent`) is a large mechanical diff for zero functional gain — the
override mechanism doesn't care what the variable is called. Flagged as
optional future cleanup, not part of this plan.

### 2.3 Fonts

Add one Google font import in `layout.tsx` for the peptide display face
(something with a clinical/technical character, distinct from Fraunces'
editorial serif — e.g. a grotesk/technical family; exact pick is a design
call, not an engineering one). Body and mono stay shared across every
vertical (Space Grotesk / IBM Plex Mono already read fine in the peptide
homepage's mono labels) — only the display face varies by kind.

Font loading is scoped to the active storefront, not global, so this doesn't
get more expensive as more verticals are added: `layout.tsx` already knows
`storefront.kind` at render time (it's resolved server-side before the
`<html>` tag is written), so only the display-font className matching the
current kind is applied to `<html>`:

```ts
const DISPLAY_FONT_CLASS: Record<string, string> = {
    dispensary: fraunces.variable,
    hash: fraunces.variable,       // alias until hash gets its own face
    footwear: fraunces.variable,   // alias until footwear gets its own face
    peptides: peptideDisplay.variable,
}
// ...
className={`${DISPLAY_FONT_CLASS[storefront.kind] ?? fraunces.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
```

Each `next/font/google` call is still a static import (a Next.js
requirement — you cannot pick which font to import at runtime), so every
display font used by *any* live storefront is still part of the build
output. What this pattern avoids is a single visitor's browser fetching
every vertical's display font on every page load: a dispensary visitor's
`<html>` only carries the Fraunces variable class, so Next never emits or
requests the peptide font's `@font-face` for that request, and vice versa.
Net effect: adding a 5th storefront kind adds its display font to the build,
not to every visitor's download. `--font-hc-display` itself is what gets
swapped per vertical in the CSS block above, so no component that uses
`font-hc-display` needs to change regardless of how many kinds exist.

### 2.4 Radius / shape language

`--radius` (already a real variable feeding shadcn's `--radius-sm/md/lg/xl`)
gets a smaller value under `[data-vertical="peptides"]` — sharper corners on
buttons, inputs, cards site-wide, reinforcing "clinical" vs dispensary's
soft/rounded language, again with no component edits.

---

## 3. Tier 2: token-hygiene fixes (make the override actually reach everything)

Two components hardcode literals instead of referencing the token system, so
the Section 2 override won't touch them. These need real edits:

- **`src/components/shop/ProductCard.tsx`** — replace
  `from-[#fbf7ee] to-hc-paper-2` with a token pair (e.g. add
  `--color-hc-paper-3` for the lighter gradient stop, or just use
  `from-hc-paper to-hc-paper-2`), and replace the raw
  `shadow-[...rgba(23,20,15,...)]` with an `rgb(from var(--color-hc-ink) r g
  b / .35)` (Tailwind v4 supports CSS relative color syntax) or a themed
  `--shadow-hc-card` variable.
- **`src/components/home/JarCard.tsx`** — same gradient/shadow fix. Only
  used on the dispensary homepage today, lower urgency, but same 10-minute
  fix while touching the file.
- **`src/components/layout/Logo.tsx`** — the peptide fallback badge
  (hardcoded `#9ee8ce`, hardcoded "A") is replaced with a theme-driven
  wordmark: initial letter from `storefront.name`, accent color from
  `var(--color-hc-amber-light)`. This also makes the fallback correct for
  any future kind that has no `logo_url`, not just peptides.

`src/components/icons/EffectIcons.tsx` hex values are intentionally left
alone — those are cannabis effect-tag colors (happy/relaxed/sleepy/...), a
content taxonomy, not a storefront brand token. Not in scope.

---

## 4. Tier 3: structural/content divergence (case-by-case, as agreed)

Judgment calls on where a re-theme isn't enough and the component itself
should differ:

1. **Product card motif** (`ProductCard.tsx`). The rotate-on-hover,
   rounded-22px, warm-gradient "jar card" is a dispensary-specific motif, not
   a neutral shape that happens to be amber-colored. Recommendation: gate the
   motif behind `theme.productCardVariant` — dispensary keeps `organic`
   (current behavior, unchanged), peptides gets `clinical` (flat card,
   sharper corners via the Section 2.4 `--radius` change, no rotate
   transform, thin 1px border instead of the colored drop shadow). This is a
   single `cn()` branch inside the existing component, not a new file — the
   stat-row logic (THC vs purity/format) already branches correctly and
   stays as-is.
2. **Peptide product-detail content** (new file, mirrors the existing
   pattern exactly): `src/verticals/peptides/PeptideProductContent.tsx`
   exporting `PeptideSpecs` (purity/concentration/form/COA link, sourced from
   `product.vertical_profile.data`, same shape `CannabisProductSpecs`
   already reads for cannabis) and `PeptideBlogLink` ("Research notes on our
   blog" instead of "Cannabis basics"). Wired into `ProductDetails.tsx`
   behind `features.peptideCatalog`, next to the existing
   `features.cannabisCatalog` branch. This closes the "peptide product pages
   are blank" gap from Section 1, not just a visual fix.
3. **Homepage** — already fully bespoke (`PeptideHome.tsx`/`page.tsx`
   branch). No change needed structurally; only the color literals inside it
   move to the theme tokens from Section 2.1 so the homepage and the rest of
   the site draw from one palette instead of two.
4. Everything else audited (Navbar, Footer, CartDrawer, checkout steps, blog,
   FAQ, legal pages) has no cannabis-specific *structure* — only cannabis
   *coloring* — so token override alone is correct for them. No structural
   variant needed.

---

## 5. Reusable component inventory

Components confirmed truly storefront-agnostic (no kind-specific content or
motif; theme tokens fully cover them) — safe to leave untouched by this
work:

- `components/ui/*` (shadcn primitives — badge, card, button, etc.)
- `components/layout/navbar/*` except `constants.ts` data (which already
  branches correctly via `NAV_LINKS`/`PEPTIDE_NAV_LINKS`)
- `components/layout/SiteShell.tsx`, `Footer.tsx` (structure is shared;
  content already branches via `FEATURES`/column maps)
- `components/shop/CartDrawer.tsx`, `ProductsGrid.tsx`, `CategoryGrid.tsx`,
  `BrandStrip.tsx`, `FeaturedProducts.tsx`
- `components/checkout/*` (all steps — no raw hex found, pure token usage)
- `components/blog/*`, `components/support/*`
- `components/providers/*`, `hooks/*`, `store/*`, `lib/*`

Components with kind-specific **content** that already branch correctly
(pattern to replicate for peptides in Tier 3, not to rebuild):

- `verticals/cannabis/CannabisProductContent.tsx` — the model for
  `PeptideProductContent.tsx`
- `components/layout/Footer.tsx` internal column maps
- `components/layout/navbar/constants.ts` nav link arrays
- `storefront/config.ts` `FEATURES` map — the model for `theme.ts`

Components needing the Tier 2 hygiene fix before they're truly
theme-portable:

- `components/shop/ProductCard.tsx`
- `components/home/JarCard.tsx`
- `components/layout/Logo.tsx`

---

## 6. Rollout order (no big-bang, each step independently shippable/testable)

1. Add `src/storefront/theme.ts` with `dispensary` entry only (values copied
   from current `@theme` block) — no visual change, just establishes the
   contract.
2. Add the `html[data-vertical="peptides"]` override block in `globals.css`
   using the palette already in `PeptideHome.tsx` — visually reskins the
   shared UI (nav/footer/cart/checkout/blog/legal) for peptides for the
   first time. Verify against a running peptide storefront before touching
   anything else.
3. Tier 2 hygiene fixes (`ProductCard`, `JarCard`, `Logo`) — needed before
   step 2's override reaches the product grid correctly.
4. Add peptide display font + `--font-hc-display` override.
5. `ProductCard` clinical variant (Tier 3.1).
6. `PeptideProductContent.tsx` + `ProductDetails.tsx` wiring (Tier 3.2).
7. Refactor `PeptideHome.tsx` literals to reference the Section 2 tokens
   instead of inline hex (cosmetic cleanup, confirms the token set is
   complete).

Each step is a small, reviewable diff against a real running instance,
consistent with how backend changes in this project get validated before
committing.

---

## 7. Reproducing this for future storefronts

The architecture is designed so most of a new storefront kind's identity is
a config addition. This section is the honest split of what's free versus
what's bespoke work each time, and a runbook for the free part.

### 7.1 Config-only (no new component code, same effort as flipping a flag)

- **`theme.ts`** — one new object literal: colors, radius, font pick,
  `productCardVariant`.
- **`globals.css`** — one new `html[data-vertical="X"] { ... }` block,
  values pulled straight from the `theme.ts` entry.
- **`layout.tsx`** — one new row in the `DISPLAY_FONT_CLASS` map (Section
  2.3) if the new kind gets its own display font; one new `next/font/google`
  call if that font isn't already imported for another kind.
- **`FEATURES`** (`storefront/config.ts`) — one new row, or point the new
  kind at an existing row if it shares behavior (this already happens today:
  `hash` aliases `dispensary`'s flags).
- **`navbar/constants.ts`** — one new `<KIND>_NAV_LINKS` array, same shape
  as `PEPTIDE_NAV_LINKS`.
- **`Footer.tsx`** — one new `<KIND>_COLUMNS` map plus, if the vertical
  needs its own legal disclaimer text, one new `features.<kind>Catalog &&
  <p>...</p>` block next to the existing two.
- **Logo fallback** — automatic. After the Tier 2 fix (Section 3), the
  no-`logo_url` fallback badge derives its initial letter and accent color
  from `storefront.name` and the active theme tokens, so a brand-new kind
  gets a correct fallback with zero code.
- **Metadata / favicon branching in `layout.tsx`** — one new case in the
  existing `storefront.kind === 'peptides' ? ... : ...` ternaries. Small,
  but worth calling out: these are still if/else chains, not a lookup table,
  so this is the one "config-only" item that currently requires editing an
  expression rather than adding a row. Low risk to convert to a
  `Record<kind, ...>` lookup at the same time a third kind is added, if you
  want that cleaned up then.

None of the above touches `ProductCard.tsx`, `Navbar.tsx`, `CartDrawer.tsx`,
the checkout steps, blog, or legal pages — they read the tokens and content
maps above without knowing how many kinds exist.

### 7.2 Bespoke per storefront (same order of effort as the Peptides work in this plan)

- **Homepage.** A new `verticals/<kind>/<Kind>Home.tsx` plus a new branch in
  `app/page.tsx`. This is inherent to "a real different layout" — there's no
  way to make a genuinely different homepage a config row, the same way
  `PeptideHome.tsx` itself isn't one.
- **Vertical-specific product content**, if the new kind's products carry
  attributes cannabis/peptides don't (footwear: size/color/material; hash:
  different lab fields). One new `verticals/<kind>/<Kind>ProductContent.tsx`
  mirroring `CannabisProductContent.tsx` / `PeptideProductContent.tsx`,
  wired into `ProductDetails.tsx` behind its own feature flag. If the new
  kind's products fit the existing cannabis or peptide shape closely enough,
  this step can be skipped and the existing content reused — worth checking
  before building a new one.
- **`ProductCard` variant**, only if `organic`/`clinical` don't fit. Adding
  a third variant is one more branch in the existing `cn()` logic in
  `ProductCard.tsx`, not a new component.

### 7.3 Runbook: adding a new live storefront kind

1. Confirm whether the new kind's product content fits `cannabis` or
   `peptide` shape, or needs its own `<Kind>ProductContent.tsx` (Section
   7.2).
2. Add the `theme.ts` entry (colors, radius, font, card variant).
3. Add the `globals.css` override block from the `theme.ts` values.
4. Add the font import + `DISPLAY_FONT_CLASS` row (skip if reusing an
   existing display font).
5. Add `FEATURES` row, nav links, footer columns/disclaimer.
6. Build the homepage (`verticals/<kind>/<Kind>Home.tsx` + `page.tsx`
   branch).
7. If step 1 needs a new content component, build and wire it into
   `ProductDetails.tsx`.
8. Verify against a running instance of that storefront before committing —
   same validation standard as the rest of this plan.

Steps 2, 3, 5 are the "config-only" tier and are quick. Steps 1, 6, 7 are
the real design/build work and take roughly as long as the Peptides-specific
items in this plan (Tier 3, Section 4) did.

---

## 8. Open items for you to confirm before I start building

- Peptide display font pick — any preference, or should I propose 2-3
  options for you to pick from?
- Exact peptide palette — use the values already in `PeptideHome.tsx`
  verbatim (as drafted above), or do you want to adjust any of them while
  we're formalizing them as the permanent theme?
- `ProductCard` clinical variant — confirm no-rotate/flat-border/sharper
  corners is the direction, or you have a different concrete visual in mind.
