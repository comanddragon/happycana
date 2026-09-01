// app/lab-results/page.tsx
import type { Metadata } from 'next'
import Link from 'next/link'
import { FileText, ArrowLeft, ArrowRight } from 'lucide-react'
import { getLabResults } from '@/lib/catalog.server'
import { formatThc, formatWeight, mediaUrl, CANNABIS_TYPE_LABEL, POTENCY_LABEL } from '@/lib/utils'

export const metadata: Metadata = {
    title: 'Lab Results',
    description: 'Every product with an on-file certificate of analysis, in one place — real batch data, not just a badge.',
    alternates: { canonical: '/lab-results' },
}

interface PageProps {
    searchParams: Promise<{ page?: string }>
}

export default async function LabResultsPage({ searchParams }: PageProps) {
    const { page } = await searchParams
    const pageNum = Number(page) > 1 ? Number(page) : 1
    const { results, count } = await getLabResults(pageNum)
    const pageSize = 20
    const hasNext = pageNum * pageSize < count
    const hasPrev = pageNum > 1

    return (
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
            <Link href="/" className="font-hc-mono text-xs tracking-wide text-hc-ink-soft hover:text-hc-amber-dim">
                &larr; HOME
            </Link>
            <p className="mt-4 font-hc-mono text-xs tracking-wide text-hc-sage-dim">LAB TESTING</p>
            <h1 className="mt-2 font-hc-display text-4xl font-medium text-hc-ink">Lab Results</h1>
            <p className="mt-3 max-w-2xl text-hc-ink-soft leading-relaxed">
                Every product below has a real, on-file certificate of analysis from an independent lab. This
                page lists them all in one place — click through to a product to see its full COA.
            </p>

            {results.length === 0 ? (
                <p className="mt-12 text-hc-ink-soft">No lab results are on file yet.</p>
            ) : (
                <div className="mt-10 divide-y divide-hc-ink/[0.08] rounded-2xl border border-hc-ink/[0.08] bg-white">
                    {results.map(result => {
                        const weight = formatWeight(result.weight_value, result.weight_unit)
                        const thc = formatThc(result.lab.thc_percent)
                        const kind = result.product.cannabis_type
                            ? CANNABIS_TYPE_LABEL[result.product.cannabis_type]
                            : null
                        return (
                            <div key={result.id} className="flex items-center gap-4 px-5 py-4">
                                {result.product.primary_image?.image_url && (
                                    // eslint-disable-next-line @next/next/no-img-element
                                    <img
                                        src={mediaUrl(result.product.primary_image.image_url) ?? undefined}
                                        alt={result.product.primary_image.alt_text || result.product.name}
                                        className="h-12 w-12 shrink-0 rounded-lg object-cover"
                                    />
                                )}
                                <div className="min-w-0 flex-1">
                                    <Link
                                        href={`/shop/products/${result.product.slug}`}
                                        className="font-hc-display text-base font-medium text-hc-ink hover:text-hc-amber-dim"
                                    >
                                        {result.product.name}
                                    </Link>
                                    <p className="mt-0.5 font-hc-mono text-[11px] tracking-wide text-hc-ink-soft">
                                        {[result.product.brand?.name, kind, weight, thc, result.lab.potency && POTENCY_LABEL[result.lab.potency]]
                                            .filter(Boolean)
                                            .join(' · ')}
                                    </p>
                                </div>
                                <a
                                    href={result.lab.coa_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex shrink-0 items-center gap-1.5 rounded-full border border-hc-ink/[0.1] px-3 py-1.5 font-hc-mono text-[11px] font-medium text-hc-amber-dim transition-colors hover:border-hc-amber"
                                >
                                    <FileText className="h-3.5 w-3.5" />
                                    COA
                                </a>
                            </div>
                        )
                    })}
                </div>
            )}

            {(hasPrev || hasNext) && (
                <div className="mt-6 flex items-center justify-between">
                    {hasPrev ? (
                        <Link href={`/lab-results?page=${pageNum - 1}`} className="flex items-center gap-1 text-sm font-medium text-hc-amber-dim hover:underline">
                            <ArrowLeft className="h-4 w-4" /> Previous
                        </Link>
                    ) : <span />}
                    {hasNext && (
                        <Link href={`/lab-results?page=${pageNum + 1}`} className="flex items-center gap-1 text-sm font-medium text-hc-amber-dim hover:underline">
                            Next <ArrowRight className="h-4 w-4" />
                        </Link>
                    )}
                </div>
            )}
        </div>
    )
}
