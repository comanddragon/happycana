// components/blog/BlogArticle.tsx
// Shared shell for /blog/[slug] pages. Handles everything that's the same
// across every post \u2014 breadcrumb, tag pills, meta row, optional TL;DR
// callout and table of contents, Article JSON-LD, author bio, and a
// "keep reading" footer \u2014 so each post file only supplies its own body.
import Link from 'next/link'
import { BLOG_POSTS, AUTHORS, formatPostDate, type BlogPost } from '@/lib/blog'

interface TocItem {
    id: string
    label: string
}

interface Props {
    post: BlogPost
    children: React.ReactNode
    /** TL;DR shown in the amber callout right under the intro. Omit to skip it. */
    tldr?: string
    /** Table of contents entries; each must match a heading's `id` in the body. */
    toc?: TocItem[]
    /** Slugs to surface as "keep reading" at the bottom. Defaults to the other posts. */
    relatedSlugs?: string[]
}

export function BlogArticle({ post, children, tldr, toc, relatedSlugs }: Props) {
    const author = AUTHORS[post.author]
    const related = (relatedSlugs
        ? relatedSlugs.map(slug => BLOG_POSTS.find(p => p.slug === slug)).filter(Boolean)
        : BLOG_POSTS.filter(p => p.slug !== post.slug).slice(0, 2)) as BlogPost[]

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: post.title,
        description: post.description,
        datePublished: post.publishedAt,
        author: { '@type': 'Person', name: author.name },
    }

    return (
        <article className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />

            <Link href="/blog" className="font-hc-mono text-xs tracking-wide text-hc-ink-soft hover:text-hc-amber-dim">
                &larr; BLOG
            </Link>

            <div className="mt-4 flex flex-wrap gap-2">
                {post.tags.map(tag => (
                    <span
                        key={tag}
                        className="rounded-full border border-hc-ink/[0.08] bg-white px-3 py-1 font-hc-mono text-[10.5px] uppercase tracking-wide text-hc-sage-dim"
                    >
                        {tag}
                    </span>
                ))}
            </div>

            <h1 className="mt-4 font-hc-display text-4xl font-medium leading-tight text-hc-ink">{post.title}</h1>

            <div className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1 font-hc-mono text-xs tracking-wide text-hc-ink-soft">
                <span>By {author.name}</span>
                <span aria-hidden>&middot;</span>
                <span>{formatPostDate(post.publishedAt)}</span>
                <span aria-hidden>&middot;</span>
                <span>{post.readTime} read</span>
            </div>

            {toc && toc.length > 0 && (
                <nav className="mt-8 rounded-2xl border border-hc-ink/[0.08] bg-hc-paper-2 p-5">
                    <p className="mb-3 font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-sage-dim">
                        Table of contents
                    </p>
                    <ol className="space-y-1.5">
                        {toc.map((item, i) => (
                            <li key={item.id}>
                                <a
                                    href={`#${item.id}`}
                                    className="text-sm text-hc-ink-soft hover:text-hc-amber-dim transition-colors"
                                >
                                    {i + 1}. {item.label}
                                </a>
                            </li>
                        ))}
                    </ol>
                </nav>
            )}

            {tldr && (
                <div className="mt-8 rounded-2xl border border-hc-amber/30 bg-hc-amber-light/15 p-5">
                    <p className="font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-amber-dim">TL;DR</p>
                    <p className="mt-2 leading-relaxed text-hc-ink">{tldr}</p>
                </div>
            )}

            <div
                className="
                    mt-10 space-y-8 text-hc-ink-soft
                    [&_h2]:font-hc-display [&_h2]:text-xl [&_h2]:font-medium [&_h2]:text-hc-ink [&_h2]:mb-2 [&_h2]:scroll-mt-24
                    [&_h3]:font-hc-display [&_h3]:text-base [&_h3]:font-medium [&_h3]:text-hc-ink [&_h3]:mb-1
                    [&_p]:leading-relaxed
                    [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1
                    [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1
                    [&_li]:leading-relaxed
                    [&_strong]:text-hc-ink [&_strong]:font-semibold
                    [&_table]:w-full [&_table]:border-collapse [&_table]:overflow-hidden [&_table]:rounded-xl [&_table]:border [&_table]:border-hc-ink/[0.08]
                    [&_th]:bg-hc-paper-2 [&_th]:px-4 [&_th]:py-2.5 [&_th]:text-left [&_th]:font-hc-mono [&_th]:text-[11px] [&_th]:uppercase [&_th]:tracking-wide [&_th]:text-hc-sage-dim
                    [&_td]:border-t [&_td]:border-hc-ink/[0.08] [&_td]:px-4 [&_td]:py-2.5 [&_td]:text-sm
                "
            >
                {children}
            </div>

            <div className="mt-14 flex items-start gap-4 rounded-2xl border border-hc-ink/[0.08] bg-hc-paper-2 p-6">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-hc-canopy font-hc-display text-sm text-hc-amber-light">
                    {author.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                    <p className="font-hc-display text-sm font-medium text-hc-ink">{author.name}</p>
                    <p className="font-hc-mono text-[10.5px] uppercase tracking-wide text-hc-sage-dim">{author.role}</p>
                    <p className="mt-2 text-sm leading-relaxed text-hc-ink-soft">{author.bio}</p>
                </div>
            </div>

            {related.length > 0 && (
                <div className="mt-16 border-t border-hc-ink/[0.08] pt-8">
                    <p className="mb-4 font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-sage-dim">
                        Keep reading
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2">
                        {related.map(p => (
                            <Link
                                key={p.slug}
                                href={`/blog/${p.slug}`}
                                className="rounded-xl border border-hc-ink/[0.08] bg-white p-4 text-sm font-medium text-hc-ink transition-colors hover:border-hc-amber"
                            >
                                {p.title}
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </article>
    )
}
