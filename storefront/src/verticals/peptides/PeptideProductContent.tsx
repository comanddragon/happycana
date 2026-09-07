'use client'

import Link from 'next/link'
import { BookOpen, ChevronRight, ExternalLink, FileText } from 'lucide-react'
import { Card } from '@/components/ui/card'
import type { Product } from '@/types'

export function PeptideProductSpecs({ product }: { product: Product }) {
    const profile = product.vertical_profile?.kind === 'peptide'
        ? product.vertical_profile.data
        : null
    if (!profile) return null

    const rows: { label: string; value: string }[] = []
    if (profile.purity_percent) rows.push({ label: 'Purity', value: `${Number(profile.purity_percent).toFixed(1)}%` })
    if (profile.concentration) rows.push({ label: 'Concentration', value: profile.concentration })
    if (profile.form) rows.push({ label: 'Format', value: profile.form })
    if (profile.molecular_weight) rows.push({ label: 'Molecular weight', value: profile.molecular_weight })
    if (profile.sequence) rows.push({ label: 'Sequence', value: profile.sequence })
    if (profile.storage_requirements) rows.push({ label: 'Storage', value: profile.storage_requirements })

    if (!rows.length && !profile.documentation_url) return null
    return (
        <div className="space-y-3">
            {!!rows.length && (
                <Card className="divide-y overflow-hidden">
                    {rows.map(row => (
                        <div key={row.label} className="flex justify-between gap-6 px-4 py-3 text-sm">
                            <span className="shrink-0 text-muted-foreground">{row.label}</span>
                            <span className="break-words text-right font-medium">{row.value}</span>
                        </div>
                    ))}
                </Card>
            )}
            {profile.documentation_url && (
                <a href={profile.documentation_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm font-medium text-hc-amber-dim transition-colors hover:text-hc-amber">
                    <FileText className="h-4 w-4" />
                    View source documentation
                    <ExternalLink className="h-3.5 w-3.5" />
                </a>
            )}
        </div>
    )
}

export function PeptideBlogLink() {
    return (
        <Link href="/blog" className="flex items-center gap-2 rounded-lg bg-muted px-4 py-3 text-sm font-medium text-hc-ink transition-colors hover:bg-muted/70">
            <BookOpen className="h-4 w-4 shrink-0 text-hc-amber-dim" />
            <span className="truncate">Research notes and handling guides</span>
            <ChevronRight className="ml-auto h-4 w-4 shrink-0 text-muted-foreground" />
        </Link>
    )
}
