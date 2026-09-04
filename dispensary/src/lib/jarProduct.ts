// lib/jarProduct.ts
// Maps a real catalog Product to the JarCard display shape. Used by the
// homepage Hero and BatchGrid so the decorative "jar" cards show actual
// product/lab data (and link to the real product page) instead of
// hardcoded placeholder claims.

import type { JarProduct } from '@/components/home/JarCard'
import { formatPrice, formatThc, formatWeight, CANNABIS_TYPE_LABEL } from '@/lib/utils'
import type { Product } from '@/types'

export function toJarProduct(product: Product): JarProduct {
    const variant = product.variants?.[0] ?? null
    const lab = variant?.lab ?? null

    const topTerpene = Object.entries(lab?.terpenes?.terpenes ?? {})
        .filter(([, v]) => v?.value != null)
        .sort(([, a], [, b]) => (b.value ?? 0) - (a.value ?? 0))[0]?.[0] ?? null

    return {
        name: product.name,
        slug: product.slug,
        kind: product.cannabis_type ? CANNABIS_TYPE_LABEL[product.cannabis_type] ?? null : null,
        thc: formatThc(lab?.thc_percent),
        terpene: topTerpene,
        effect: product.effects?.[0]?.name ?? null,
        brand: product.brand?.name ?? null,
        category: product.category?.[0]?.name ?? null,
        weight: formatWeight(variant?.weight_value, variant?.weight_unit),
        sku: variant?.sku ?? product.slug,
        coaUrl: lab?.coa_url || null,
        price: variant
            ? `${formatPrice(variant.price)}${formatWeight(variant.weight_value, variant.weight_unit) ? ` / ${formatWeight(variant.weight_value, variant.weight_unit)}` : ''}`
            : formatPrice(product.base_price),
    }
}
