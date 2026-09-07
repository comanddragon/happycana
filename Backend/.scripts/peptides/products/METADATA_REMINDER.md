# Meta title/description reminder

`seed_products.py` currently uses the scraped `meta_title`/`meta_description`
columns from `products.csv` verbatim (truncated to 60/160 chars) whenever
they're present, instead of falling back to the generated title/description.

That's a duplicate-content and copyright risk: publishing the source site's
own SEO copy unchanged means our product pages can carry byte-for-byte the
same `<title>`/meta description as peptidessource.com's equivalent pages,
which search engines can treat as duplicate content (they may discard our
meta description and auto-generate a snippet instead, so we lose control of
our own search listing), and it's someone else's written copy either way.

## To do

If you want SEO copy that's actually better than the generated template, the
right move is to feed the scraped title/description into a rewrite step
(LLM-generated, our own brand voice, our own differentiators) rather than
pass it through unchanged.

Not wired up yet -- ask Claude to build this when ready. Shape TBD, but
likely: a rewrite pass (batched LLM call over `products.csv`) that reads
`meta_title`/`meta_description` as *reference input* alongside the product
name/category/form, and writes new `rewritten_meta_title` /
`rewritten_meta_description` columns for `seed_products.py` to prefer
instead of the raw scraped columns.
