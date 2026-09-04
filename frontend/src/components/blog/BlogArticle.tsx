// components/blog/BlogArticle.tsx
// Shared shell for /blog/[slug] pages. Handles the parts that are the same
// across every post — breadcrumb, tag pills, meta row, Article JSON-LD, and
// the post body itself — sourced from the backend BlogPost API rather than
// hand-authored JSX, so a new post just needs a row in the database.
import Link from 'next/link'
import type { BlogPostDetail } from '@/types'
import { formatPostDate } from '@/lib/blog.server'
import { BlogContent } from '@/components/blog/BlogContent'

interface Props {
    post: BlogPostDetail
}

export function BlogArticle({ post }: Props) {
    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: post.title,
        description: post.description,
        datePublished: post.published_at,
        ...(post.updated_at && { dateModified: post.updated_at }),
        // image/publisher are what Google's rich-result validator checks
        // for Article eligibility — both were missing before.
        ...(post.image && { image: [post.image] }),
        publisher: {
            '@type': 'Organization',
            name: 'HappyCana',
            ...(process.env.NEXT_PUBLIC_FRONTEND_URL && {
                logo: { '@type': 'ImageObject', url: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/favicon.ico` },
            }),
        },
        ...(post.author ? { author: { '@type': 'Person', name: post.author } } : {}),
        mainEntityOfPage: `${process.env.NEXT_PUBLIC_FRONTEND_URL ?? ''}/blog/${post.slug}`,
    }
    const breadcrumbLd = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Home', item: process.env.NEXT_PUBLIC_FRONTEND_URL },
            { '@type': 'ListItem', position: 2, name: 'Blog', item: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/blog` },
            { '@type': 'ListItem', position: 3, name: post.title, item: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/blog/${post.slug}` },
        ],
    }

    return (
        <article className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }} />

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

            <BlogContent html={post.content_html} />
        </article>
    )
}
