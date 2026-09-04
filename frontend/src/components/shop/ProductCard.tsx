'use client'

import { memo, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { ShoppingBag, Plus } from 'lucide-react'
import { cn, formatPrice, mediaUrl, formatWeight, formatThc, CANNABIS_TYPE_LABEL, COMPLIANCE_CATEGORY_LABEL } from '@/lib/utils'
import { useAddToCart } from '@/hooks/useApi'
import type { Product } from '@/types'

interface Props { product: Product; className?: string; priority?: boolean }

export const ProductCard = memo(function ProductCard({ product, className, priority = false }: Props) {
    const router        = useRouter()
    const addToCart      = useAddToCart()
    const [imageLoaded, setImageLoaded] = useState(priority)
    const firstVariant   = product.variants?.[0]
    const category       = product.category?.[0] ?? null
    // Prefer product-level primary image, fall back to first image, then variant image
    const displayImage = mediaUrl(
        product.primary_image?.image_url ??
        product.images?.[0]?.image_url ??
        firstVariant?.primary_image?.image_url
    )

    const displayPrice = firstVariant ? formatPrice(firstVariant.price) : formatPrice(product.base_price)
    const regularPrice = Number(firstVariant?.price ?? product.base_price)
    const discount = product.active_discount
    const importedOriginalPrice = Number(product.compare_at_price ?? 0)
    const discountedPrice = discount
        ? Math.max(0, discount.discount_type === 'percent'
            ? regularPrice * (1 - Number(discount.value) / 100)
            : regularPrice - Number(discount.value))
        : null
    const discountLabel = discount
        ? discount.discount_type === 'percent'
            ? `${Number(discount.value).toLocaleString()}% OFF`
            : `${formatPrice(discount.value)} OFF`
        : null
    const hasMultiplePrices = product.variants?.length > 1 &&
        product.variants.some(v => v.price !== product.variants[0].price)

    // The jar-card's signature stat row — sourced from the real
    // brand/classification/lab/weight fields rather than the old generic
    // EAV attributes (which are empty for the seeded catalog now that
    // those values live in their own columns; see MISSING_FIELDS.md).
    const typeLabel = product.cannabis_type
        ? CANNABIS_TYPE_LABEL[product.cannabis_type]
        : product.compliance_category
            ? COMPLIANCE_CATEGORY_LABEL[product.compliance_category]
            : product.sub_type || null
    const thcLabel     = formatThc(firstVariant?.lab?.thc_percent)
    const weightLabel  = formatWeight(firstVariant?.weight_value, firstVariant?.weight_unit)
    const stats = [
        thcLabel && { label: 'THC', value: thcLabel.replace('% THC', '%') },
        typeLabel && { label: 'TYPE', value: typeLabel },
        weightLabel && { label: 'SIZE', value: weightLabel },
    ].filter((s): s is { label: string; value: string } => Boolean(s)).slice(0, 3)

    return (
        <div
            className={cn(
                'group relative min-w-0 rounded-[22px] bg-gradient-to-b from-[#fbf7ee] to-hc-paper-2 p-3.5 pt-5 text-hc-ink shadow-[0_20px_40px_-24px_rgba(23,20,15,0.35)] transition-transform duration-300 hover:-translate-y-1.5 hover:rotate-[-0.6deg] hover:shadow-[0_28px_48px_-20px_rgba(23,20,15,0.32)]',
                className,
            )}
        >
            {discountLabel && (
                <span className="absolute -top-3 left-1/2 z-20 -translate-x-1/2 whitespace-nowrap rounded-full bg-gradient-to-b from-hc-amber-light to-hc-amber px-3 py-1 font-hc-mono text-[10px] font-bold tracking-wide text-hc-canopy-2 shadow-sm">
                    {discountLabel}
                </span>
            )}

            <Link href={`/shop/products/${product.slug}`} className="block">
                <div className="relative aspect-square overflow-hidden rounded-2xl bg-white">
                    {displayImage ? (
                        <Image src={displayImage} alt={product.primary_image?.alt_text || product.name}
                               fill
                               quality={65}
                               decoding="async"
                               sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
                               priority={priority}
                               loading={priority ? undefined : 'lazy'}
                               onLoad={() => setImageLoaded(true)}
                               className={cn(
                                   'object-cover bg-white transition-all duration-300 group-hover:scale-105',
                                   imageLoaded ? 'opacity-100' : 'opacity-0',
                               )} />
                    ) : (
                        <div className="h-full w-full flex items-center justify-center">
                            <ShoppingBag className="h-10 w-10 text-hc-ink-soft/40" />
                        </div>
                    )}
                    {category && (
                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                router.push(category.is_key
                                    ? `/shop/categories/${category.slug}`
                                    : `/shop/collections/${category.slug}`);
                            }}
                            className="absolute left-2.5 top-2.5 flex min-h-6 items-center rounded-full z-10 bg-hc-canopy/90 px-2.5 py-1.5 font-hc-mono text-[10px] tracking-wide text-hc-sage backdrop-blur-sm"
                        >
                            {category.name}
                        </button>
                    )}
                </div>

                <div className="mt-3.5 flex items-start justify-between gap-2">
                    <div className="min-w-0">
                        {product.brand && (
                            <p className="font-hc-mono text-[10.5px] tracking-wide text-hc-ink-soft uppercase truncate">
                                {product.brand.name}
                            </p>
                        )}
                        <h2 className="font-hc-display text-[17px] font-medium leading-snug line-clamp-2 group-hover:text-hc-amber-dim transition-colors">
                            {product.name}
                        </h2>
                    </div>
                </div>

                {stats.length > 0 && (
                    <div className="mt-3 flex flex-col gap-1 sm:flex-row sm:gap-4 font-hc-mono text-[11px] text-hc-ink-soft">
                        {stats.map(stat => (
                            <div key={stat.label} className="flex min-w-0 items-baseline gap-1 sm:block">
                                <b className="truncate text-[14px] text-hc-ink sm:block">{stat.value}</b>
                                <span>{stat.label}</span>
                            </div>
                        ))}
                    </div>
                )}

                <div className="my-3.5 h-px bg-hc-ink/10" />

                <div className="flex items-center justify-between">
                    <p className="flex flex-wrap items-baseline gap-1.5 font-hc-mono text-sm font-medium text-hc-amber-dim">
                        {hasMultiplePrices && <span className="text-hc-ink-soft font-normal mr-1">from</span>}
                        {importedOriginalPrice > regularPrice ? displayPrice : discountedPrice !== null ? formatPrice(discountedPrice) : displayPrice}
                        {(importedOriginalPrice > regularPrice || discountedPrice !== null) && (
                            <span className="text-xs font-normal text-hc-ink-soft line-through">
                                {formatPrice(importedOriginalPrice > regularPrice ? importedOriginalPrice : regularPrice)}
                            </span>
                        )}
                    </p>
                    {product.variants?.length > 1 && (
                        <span className="font-hc-mono text-[10.5px] tracking-wide text-hc-ink-soft">{product.variants.length} OPTIONS</span>
                    )}
                </div>
            </Link>

            {firstVariant?.in_stock && (
                <button
                    className="absolute bottom-[4.75rem] right-4 flex h-10 w-10 items-center justify-center rounded-full text-hc-canopy-2 opacity-100 shadow-[0_8px_18px_rgba(200,121,46,.4)] transition-all duration-200 sm:opacity-0 sm:translate-y-2 sm:group-hover:opacity-100 sm:group-hover:translate-y-0 sm:group-focus-within:opacity-100 sm:group-focus-within:translate-y-0"
                    style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }}
                    onClick={() => addToCart.mutate({ variant: firstVariant.id, quantity: 1 })}
                    disabled={addToCart.isPending}
                    aria-label={`Add ${product.name} to cart`}
                >
                    <Plus className="h-4 w-4" strokeWidth={2.5} />
                </button>
            )}
        </div>
    )
})
