// components/learn/GuideArticle.tsx
// Shared shell for /learn/[guide] pages: renders the eyebrow/title header,
// an Article JSON-LD block (answer-engine and rich-result signal), the
// article body, and a "related guides" footer so every guide links to a
// couple of others instead of dead-ending.
import Link from 'next/link'
import { GUIDES, type Guide } from '@/lib/guides'

interface Props {
    guide: Guide
    children: React.ReactNode
    /** Slugs of guides to surface as "related" at the bottom. Defaults to the other guides. */
    relatedSlugs?: string[]
}

export function GuideArticle({ guide, children, relatedSlugs }: Props) {
    const related = (relatedSlugs
        ? relatedSlugs.map(slug => GUIDES.find(g => g.slug === slug)).filter(Boolean)
        : GUIDES.filter(g => g.slug !== guide.slug).slice(0, 3)) as Guide[]

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: guide.title,
        description: guide.description,
        articleSection: guide.kicker,
    }

    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />

            <Link href="/learn" className="font-hc-mono text-xs tracking-wide text-hc-ink-soft hover:text-hc-amber-dim">
                &larr; LEARN
            </Link>
            <p className="mt-4 font-hc-mono text-xs tracking-wide text-hc-sage-dim">{guide.kicker}</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">{guide.title}</h1>

            <div className="mt-10 space-y-8 text-hc-ink-soft [&_h2]:font-hc-display [&_h2]:text-xl [&_h2]:font-medium [&_h2]:text-hc-ink [&_h2]:mb-2 [&_p]:leading-relaxed [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1 [&_li]:leading-relaxed [&_strong]:text-hc-ink [&_strong]:font-semibold">
                {children}
            </div>

            {related.length > 0 && (
                <div className="mt-16 border-t border-hc-ink/[0.08] pt-8">
                    <p className="mb-4 font-hc-mono text-[11px] uppercase tracking-[0.1em] text-hc-sage-dim">
                        Keep reading
                    </p>
                    <div className="grid gap-3 sm:grid-cols-3">
                        {related.map(g => (
                            <Link
                                key={g.slug}
                                href={`/learn/${g.slug}`}
                                className="rounded-xl border border-hc-ink/[0.08] bg-white p-4 text-sm font-medium text-hc-ink transition-colors hover:border-hc-amber"
                            >
                                {g.title}
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
