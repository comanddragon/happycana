'use client'

import Link from 'next/link'
import { BookOpen, ChevronRight, FileText } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import type { Product, ProductVariant } from '@/types'
import { CANNABIS_TYPE_LABEL, COMPLIANCE_CATEGORY_LABEL, formatWeight, POTENCY_LABEL, titleCase } from '@/lib/utils'

export function CannabisBadges({ product, variant }: { product: Product; variant: ProductVariant | null }) {
    return <>{product.cannabis_type && <Badge variant="outline" className="text-xs">{CANNABIS_TYPE_LABEL[product.cannabis_type]}</Badge>}{variant?.lab?.potency && <Badge variant="outline" className="text-xs">{POTENCY_LABEL[variant.lab.potency]} potency</Badge>}</>
}

export function CannabisEffects({ product }: { product: Product }) {
    if (!product.effects.length) return null
    return <div className="flex flex-wrap gap-1.5">{product.effects.map(effect => <Link key={effect.id} href={`/shop/products?effect=${effect.slug}`}><Badge variant="secondary" className="text-xs capitalize hover:bg-hc-amber-light/15 hover:text-hc-amber-dim transition-colors cursor-pointer">{effect.name}</Badge></Link>)}</div>
}

export function CannabisProductSpecs({ product, variant }: { product: Product; variant: ProductVariant | null }) {
    const lab = variant?.lab ?? null
    const rows: { label: string; value: string }[] = []
    const weight = formatWeight(variant?.weight_value, variant?.weight_unit)
    if (weight) rows.push({ label: 'Size', value: weight })
    if (product.sub_type) rows.push({ label: 'Form', value: product.sub_type })
    if (product.compliance_category) rows.push({ label: 'Category', value: COMPLIANCE_CATEGORY_LABEL[product.compliance_category] })
    const fields: [keyof NonNullable<typeof lab>, string][] = [['thc_percent', 'THC'], ['thca_percent', 'THCa'], ['cbd_percent', 'CBD'], ['cbda_percent', 'CBDa'], ['cbn_percent', 'CBN'], ['cbg_percent', 'CBG']]
    if (lab) for (const [field, label] of fields) {
        const value = lab[field]
        if (typeof value === 'string' && value) rows.push({ label, value: `${parseFloat(value)}%` })
    }
    const terpenes = lab ? Object.entries(lab.terpenes?.terpenes ?? {}).filter(([, value]) => value?.value != null).sort(([, a], [, b]) => (b.value ?? 0) - (a.value ?? 0)).slice(0, 6) : []
    const coaUrl = lab?.coa_url || null
    if (!rows.length && !terpenes.length && !coaUrl) return null
    return <div className="space-y-3">
        {!!rows.length && <Card className="divide-y overflow-hidden">{rows.map(row => <div key={row.label} className="flex justify-between px-4 py-3 text-sm"><span className="text-muted-foreground">{row.label}</span><span className="font-medium">{row.value}</span></div>)}</Card>}
        {!!terpenes.length && <div><p className="text-sm font-semibold mb-2">Terpene profile</p><div className="flex flex-wrap gap-1.5">{terpenes.map(([name, data]) => <Badge key={name} variant="outline" className="text-xs">{titleCase(name)}{data.value != null && <span className="text-muted-foreground ml-1">{data.value}{data.unit ?? ''}</span>}</Badge>)}</div></div>}
        {coaUrl && <a href={coaUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm font-medium text-hc-amber-dim hover:text-hc-amber transition-colors"><FileText className="h-4 w-4" />View Certificate of Analysis</a>}
    </div>
}

export function CannabisBlogLink() {
    return <Link href="/blog" className="flex items-center gap-2 rounded-xl bg-muted px-4 py-3 text-sm font-medium text-hc-ink hover:bg-muted/70 transition-colors"><BookOpen className="h-4 w-4 shrink-0 text-hc-amber-dim" /><span className="truncate">Cannabis basics &amp; guides on our blog</span><ChevronRight className="h-4 w-4 shrink-0 ml-auto text-muted-foreground" /></Link>
}
