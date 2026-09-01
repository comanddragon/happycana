// components/blog/BlogArticle.tsx
// Shared shell for /blog/[slug] pages. Handles the parts that are the same
// across every post — breadcrumb, tag pills, meta row, Article JSON-LD, and
// the post body itself — sourced from the backend BlogPost API rather than
// hand-authored JSX, so a new post just needs a row in the database.
import Link from 'next/link'
import type { BlogPostDetail } from '@/types'
import { formatPostDate } from '@/lib/blog.server'

interface Props {
    post: BlogPostDetail
}

export function BlogArticle({ post }: Props) {
    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: post.title,
        description: post.description,
        datePublished: post.published_at,
        ...(post.author ? { author: { '@type': 'Person', name: post.author } } : {}),
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
                {post.author && (
                    <>
                        <span>By {post.author}</span>
                        <span aria-hidden>&middot;</span>
                    </>
                )}
                {post.published_at && (
                    <>
                        <span>{formatPostDate(post.published_at)}</span>
                        <span aria-hidden>&middot;</span>
                    </>
                )}
                <span>{post.read_time} read</span>
            </div>

            <div
                className="
                    mt-10 space-y-8 text-hc-ink-soft
                    [&_h1]:font-hc-display [&_h1]:text-2xl [&_h1]:font-medium [&_h1]:text-hc-ink [&_h1]:mb-2 [&_h1]:scroll-mt-24
                    [&_h2]:font-hc-display [&_h2]:text-xl [&_h2]:font-medium [&_h2]:text-hc-ink [&_h2]:mb-2 [&_h2]:scroll-mt-24
                    [&_h3]:font-hc-display [&_h3]:text-base [&_h3]:font-medium [&_h3]:text-hc-ink [&_h3]:mb-1
                    [&_p]:leading-relaxed
                    [&_a]:text-hc-amber-dim [&_a]:underline [&_a]:underline-offset-2
                    [&_img]:rounded-xl [&_img]:max-w-full [&_img]:h-auto
                    [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1
                    [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1
                    [&_li]:leading-relaxed
                    [&_strong]:text-hc-ink [&_strong]:font-semibold
                    [&_table]:w-full [&_table]:border-collapse [&_table]:overflow-hidden [&_table]:rounded-xl [&_table]:border [&_table]:border-hc-ink/[0.08]
                    [&_th]:bg-hc-paper-2 [&_th]:px-4 [&_th]:py-2.5 [&_th]:text-left [&_th]:font-hc-mono [&_th]:text-[11px] [&_th]:uppercase [&_th]:tracking-wide [&_th]:text-hc-sage-dim
                    [&_td]:border-t [&_td]:border-hc-ink/[0.08] [&_td]:px-4 [&_td]:py-2.5 [&_td]:text-sm
                "
                dangerouslySetInnerHTML={{ __html: post.content_html }}
            />
        </article>
    )
}
