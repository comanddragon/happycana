// app/blog/page.tsx
import type { Metadata } from 'next'
import Link from 'next/link'
import { getBlogPosts, formatPostDate } from '@/lib/blog.server'

export const metadata: Metadata = {
    title: 'Blog',
    description: 'Practical guides on cannabis accessories, rolling, and gear \u2014 what\u2019s worth owning, what to skip, and how to keep it clean.',
    alternates: { canonical: '/blog' },
}

export default async function BlogIndexPage() {
    const { results: posts } = await getBlogPosts()

    return (
        <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">BLOG</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">HappyCana Blog</h1>
            <p className="mt-3 max-w-2xl text-hc-ink-soft leading-relaxed">
                Straight talk on gear, rolling technique, and the small habits that make a session better \u2014
                written by the people who stock the shelves, not the people trying to fill them.
            </p>

            {posts.length === 0 ? (
                <p className="mt-12 text-hc-ink-soft">No posts yet — check back soon.</p>
            ) : (
                <div className="mt-12 grid gap-4 sm:grid-cols-2">
                    {posts.map(post => (
                        <Link
                            key={post.slug}
                            href={`/blog/${post.slug}`}
                            className="group flex flex-col rounded-2xl border border-hc-ink/[0.08] bg-white p-6 transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)]"
                        >
                            <div className="flex flex-wrap gap-2">
                                {post.tags.map(tag => (
                                    <span
                                        key={tag}
                                        className="rounded-full border border-hc-ink/[0.08] bg-hc-paper-2 px-2.5 py-0.5 font-hc-mono text-[10px] uppercase tracking-wide text-hc-sage-dim"
                                    >
                                        {tag}
                                    </span>
                                ))}
                            </div>
                            <h2 className="mt-3 font-hc-display text-lg font-medium text-hc-ink">
                                {post.title}
                            </h2>
                            <p className="mt-2 flex-1 text-sm leading-relaxed text-hc-ink-soft">{post.description}</p>
                            <div className="mt-4 flex items-center justify-between">
                                <span className="font-hc-mono text-[11px] tracking-wide text-hc-ink-soft">
                                    {post.author ? `${post.author} \u00b7 ` : ''}{formatPostDate(post.published_at)}
                                </span>
                                <span className="text-xs font-medium text-hc-amber-dim group-hover:underline">
                                    Read &rarr;
                                </span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
