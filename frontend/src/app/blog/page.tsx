// app/blog/page.tsx
import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { getBlogPosts } from '@/lib/blog.server'
import type { BlogPostSummary } from '@/types'

const PAGE_SIZE = 20
const PAGE_WINDOW = 1

interface PageProps {
    searchParams: Promise<{ page?: string }>
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
    const { page } = await searchParams
    const pageNum = Number(page) > 1 ? Number(page) : 1

    return {
        title: pageNum > 1 ? `Blog — Page ${pageNum}` : 'Blog',
        description: 'Practical guides on cannabis accessories, rolling, and gear \u2014 what\u2019s worth owning, what to skip, and how to keep it clean.',
        // Each paginated page canonicalizes to itself, not back to page 1 —
        // pointing every page at /blog would tell search engines that the
        // (genuinely different) posts on pages 2+ are duplicates of page
        // 1's, which suppresses crawling/indexing of everything beyond the
        // first page.
        alternates: { canonical: pageNum > 1 ? `/blog?page=${pageNum}` : '/blog' },
    }
}

function formatShortDate(iso: string | null): string {
    if (!iso) return ''
    return new Date(iso)
        .toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
        .toUpperCase()
}

export default async function BlogIndexPage({ searchParams }: PageProps) {
    const { page } = await searchParams
    const pageNum = Number(page) > 1 ? Number(page) : 1
    const { results: posts, count } = await getBlogPosts({ page: pageNum })
    const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE))

    return (
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
            <p className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">BLOG</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">HappyCana Blog</h1>
            <p className="mt-3 max-w-2xl text-hc-ink-soft leading-relaxed">
                Straight talk on gear, rolling technique, and the small habits that make a session better \u2014
                written by the people who stock the shelves, not the people trying to fill them.
            </p>

            {posts.length === 0 ? (
                <p className="mt-12 text-hc-ink-soft">No posts yet — check back soon.</p>
            ) : (
                <div className="mt-12 flex flex-col gap-14">
                    {posts.map((post, i) => (
                        <BlogRow key={post.slug} post={post} reversed={i % 2 === 1} />
                    ))}
                </div>
            )}

            {totalPages > 1 && (
                <BlogPagination currentPage={pageNum} totalPages={totalPages} />
            )}
        </div>
    )
}

function BlogRow({ post, reversed }: { post: BlogPostSummary; reversed: boolean }) {
    return (
        <article
            className={`flex flex-col gap-6 sm:gap-10 md:items-center ${
                reversed ? 'md:flex-row-reverse' : 'md:flex-row'
            }`}
        >
            <Link
                href={`/blog/${post.slug}`}
                className="block w-full shrink-0 overflow-hidden rounded-2xl md:w-1/2"
            >
                {post.image ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        src={post.image}
                        alt={post.title}
                        className="aspect-[4/3] w-full object-cover transition-transform duration-300 hover:scale-[1.03]"
                    />
                ) : (
                    <div className="aspect-[4/3] w-full bg-hc-paper-2" />
                )}
            </Link>

            <div className="w-full md:w-1/2">
                <span className="font-hc-mono text-xs tracking-wide text-hc-ink-soft">
                    {formatShortDate(post.published_at)}
                </span>

                <h2 className="mt-2 font-hc-display text-2xl font-medium leading-snug text-hc-ink">
                    <Link href={`/blog/${post.slug}`} className="hover:text-hc-amber-dim">
                        {post.title}
                    </Link>
                </h2>

                {post.author && (
                    <p className="mt-1 text-sm italic text-hc-ink-soft">by {post.author}</p>
                )}

                <p className="mt-3 text-sm leading-relaxed text-hc-ink-soft">{post.description}</p>

                {post.tags.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                        {post.tags.map(tag => (
                            <span
                                key={tag}
                                className="rounded-full border border-hc-ink/[0.08] bg-hc-paper-2 px-2.5 py-0.5 font-hc-mono text-[10px] uppercase tracking-wide text-hc-sage-dim"
                            >
                                {tag}
                            </span>
                        ))}
                    </div>
                )}

                <Link
                    href={`/blog/${post.slug}`}
                    className="mt-5 inline-flex items-center gap-1.5 rounded-full bg-hc-ink px-5 py-2.5 font-hc-mono text-[11px] font-medium uppercase tracking-wide text-hc-paper transition-colors hover:bg-hc-amber-dim"
                >
                    Continue reading
                    <ArrowRight className="h-3.5 w-3.5" />
                </Link>
            </div>
        </article>
    )
}

function BlogPagination({ currentPage, totalPages }: { currentPage: number; totalPages: number }) {
    const pages = new Set<number>([1, totalPages])
    for (let p = currentPage - PAGE_WINDOW; p <= currentPage + PAGE_WINDOW; p++) {
        if (p >= 1 && p <= totalPages) pages.add(p)
    }
    const sorted = Array.from(pages).sort((a, b) => a - b)

    const items: (number | 'ellipsis')[] = []
    sorted.forEach((p, i) => {
        if (i > 0 && p - sorted[i - 1] > 1) items.push('ellipsis')
        items.push(p)
    })

    return (
        <nav className="mt-16 flex items-center justify-center gap-2" aria-label="Blog pagination">
            {items.map((item, i) =>
                item === 'ellipsis' ? (
                    <span key={`ellipsis-${i}`} className="px-1 text-hc-ink-soft">
                        &hellip;
                    </span>
                ) : (
                    <Link
                        key={item}
                        href={item === 1 ? '/blog' : `/blog?page=${item}`}
                        aria-current={item === currentPage ? 'page' : undefined}
                        className={`flex h-8 w-8 items-center justify-center rounded-full font-hc-mono text-xs transition-colors ${
                            item === currentPage
                                ? 'bg-hc-ink text-hc-paper'
                                : 'text-hc-ink-soft hover:bg-hc-paper-2'
                        }`}
                    >
                        {item}
                    </Link>
                ),
            )}
            {currentPage < totalPages && (
                <Link
                    href={`/blog?page=${currentPage + 1}`}
                    aria-label="Next page"
                    className="ml-1 flex h-8 w-8 items-center justify-center rounded-full bg-hc-ink text-hc-paper transition-colors hover:bg-hc-amber-dim"
                >
                    <ArrowRight className="h-3.5 w-3.5" />
                </Link>
            )}
        </nav>
    )
}
