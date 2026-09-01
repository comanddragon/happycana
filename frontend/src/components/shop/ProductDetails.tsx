'use client'

import { useMemo, useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import {
    ChevronRight, ShoppingBag, Play, ImageIcon,
    Minus, Plus, Truck, RotateCcw, ShieldCheck, FileText, BookOpen,
} from 'lucide-react'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Badge }     from '@/components/ui/badge'
import { Button }    from '@/components/ui/button'
import { Card }      from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { VideoPlayer }  from '@/components/shop/VideoPlayer'
import { useAddToCart } from '@/hooks/useApi'
import { cn, formatPrice, mediaUrl, getVariantLabel, formatWeight, titleCase, CANNABIS_TYPE_LABEL, COMPLIANCE_CATEGORY_LABEL, POTENCY_LABEL } from '@/lib/utils'
import { getGuideForProduct } from '@/lib/guides'
import {
    Product,
    ProductVariant,
    ProductImage,
    ProductVideo,
    VariantImage,
    VariantVideo,
    Attribute,
} from '@/types'

type MediaItem =
    | { kind: 'image'; data: ProductImage | VariantImage; variantId?: string }
    | { kind: 'video'; data: ProductVideo | VariantVideo; variantId?: string }

export function ProductDetails({ product }: { product: Product }) {
    const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(
        product.variants?.length === 1 ? product.variants[0] : null
    )
    const [activeMedia, setActiveMedia] = useState<MediaItem | null>(null)
    const [qty, setQty]                 = useState(1)
    const addToCart                     = useAddToCart()

    const variant = selectedVariant

    // Build unified media list: product-level then per-variant
    const mediaList: MediaItem[] = useMemo(() => [
        ...product.images.map((img: ProductImage) => ({ kind: 'image' as const, data: img })),
        ...product.videos.map((vid: ProductVideo) => ({ kind: 'video' as const, data: vid })),
        ...product.variants.flatMap((v: ProductVariant) => [
            ...v.images.map((img: VariantImage) => ({ kind: 'image' as const, data: img, variantId: v.id })),
            ...v.videos.map((vid: VariantVideo) => ({ kind: 'video' as const, data: vid, variantId: v.id })),
        ]),
    ], [product])

    // Resolve which media is currently shown
    const currentMedia: MediaItem | null =
        activeMedia ??
        (variant?.primary_image
            ? { kind: 'image', data: variant.primary_image, variantId: variant.id }
            : product.primary_image
                ? { kind: 'image', data: product.primary_image }
                : product.primary_video
                    ? { kind: 'video', data: product.primary_video }
                    : mediaList[0] ?? null)

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">

            <nav className="flex items-center gap-1.5 text-sm text-muted-foreground mb-8">
                <Link href="/" className="hover:text-foreground transition-colors">Home</Link>
                <ChevronRight className="h-3.5 w-3.5" />
                <Link href="/shop/products" className="hover:text-foreground transition-colors">Products</Link>
                {product.category && (
                    <>
                        <ChevronRight className="h-3.5 w-3.5" />
                        <Link
                            href={`/shop/products?category_slug=${product.category.slug}`}
                            className="hover:text-foreground transition-colors"
                        >
                            {product.category.name}
                        </Link>
                    </>
                )}
                <ChevronRight className="h-3.5 w-3.5" />
                <span className="text-foreground font-medium truncate max-w-[180px]">{product.name}</span>
            </nav>

            <div className="grid lg:grid-cols-2 gap-12">

                <div className="space-y-3">
                    <div className="aspect-square rounded-3xl overflow-hidden bg-muted relative">
                        {currentMedia?.kind === 'video' ? (
                            <VideoPlayer video={currentMedia.data} />
                        ) : currentMedia?.kind === 'image' && currentMedia.data.image_url ? (
                            <Image
                                src={mediaUrl(currentMedia.data.image_url)!}
                                alt={currentMedia.data.alt_text || product.name}
                                fill
                                sizes="(max-width: 1024px) 100vw, 50vw"
                                priority
                                quality={85}
                                className="object-cover"
                            />
                        ) : (
                            <div className="h-full w-full flex items-center justify-center">
                                <ShoppingBag className="h-20 w-20 text-muted-foreground/20" />
                            </div>
                        )}
                    </div>

                    {mediaList.length > 1 && (
                        <ScrollArea className="w-full">
                            <div className="flex gap-2 p-2">
                                {mediaList.map((item, i) => {
                                    const isActive = activeMedia
                                        ? activeMedia.data.id === item.data.id
                                        : currentMedia?.data.id === item.data.id
                                    const belongsToOtherVariant =
                                        item.variantId !== undefined && item.variantId !== variant?.id
                                    const thumbSrc = item.kind === 'image'
                                        ? item.data.image_url
                                        : item.data.thumbnail_url

                                    return (
                                        <button
                                            key={item.data.id + i}
                                            aria-label={item.kind === 'video' ? 'View video' : 'View image'}
                                            onClick={() => {
                                                if (item.variantId) {
                                                    const v = product.variants.find((v: ProductVariant) => v.id === item.variantId)
                                                    if (v) setSelectedVariant(v)
                                                }
                                                setActiveMedia(item)
                                            }}
                                            className={cn(
                                                'relative h-16 w-16 shrink-0 rounded-xl overflow-hidden border-2 transition-all',
                                                isActive
                                                    ? 'border-hc-amber ring-2 ring-hc-amber/20'
                                                    : 'border-border hover:border-muted-foreground/40',
                                                belongsToOtherVariant && 'opacity-40',
                                            )}
                                        >
                                            {thumbSrc ? (
                                                <Image src={mediaUrl(thumbSrc)!} alt={('alt_text' in item.data ? item.data.alt_text : '') || product.name} width={64} height={64} quality={40} className="h-full w-full object-cover" />
                                            ) : (
                                                <div className="h-full w-full bg-muted flex items-center justify-center">
                                                    {item.kind === 'video'
                                                        ? <Play className="h-4 w-4 text-muted-foreground" />
                                                        : <ImageIcon className="h-4 w-4 text-muted-foreground" />}
                                                </div>
                                            )}
                                            {item.kind === 'video' && (
                                                <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                                                    <Play className="h-4 w-4 text-white drop-shadow" />
                                                </div>
                                            )}
                                        </button>
                                    )
                                })}
                            </div>
                            <ScrollBar orientation="horizontal" />
                        </ScrollArea>
                    )}
                </div>

                <div className="flex flex-col gap-5">
                    <div className="flex flex-wrap items-center gap-2">
                        {product.category && (
                            <Link href={`/shop/products?category=${product.category.slug}`}>
                                <Badge variant="secondary" className="text-xs uppercase tracking-widest">
                                    {product.category.name}
                                </Badge>
                            </Link>
                        )}
                        {product.cannabis_type && (
                            <Badge variant="outline" className="text-xs">
                                {CANNABIS_TYPE_LABEL[product.cannabis_type]}
                            </Badge>
                        )}
                        {variant?.lab?.potency && (
                            <Badge variant="outline" className="text-xs">
                                {POTENCY_LABEL[variant.lab.potency]} potency
                            </Badge>
                        )}
                    </div>

                    <div>
                        {product.brand && (
                            <Link
                                href={`/shop/products?brand=${product.brand.slug}`}
                                className="text-sm font-medium text-hc-amber-dim hover:text-hc-amber transition-colors"
                            >
                                {product.brand.name}
                            </Link>
                        )}
                        <h1 className="font-hc-display text-3xl lg:text-4xl font-medium leading-tight text-hc-ink">{product.name}</h1>
                        <p className="mt-3 text-2xl font-bold">
                            {variant ? formatPrice(variant.price) : formatPrice(product.base_price)}
                        </p>
                    </div>

                    <p className="text-muted-foreground leading-relaxed">{product.description}</p>

                    {product.effects.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                            {product.effects.map(effect => (
                                <Link key={effect.id} href={`/shop/products?effect=${effect.slug}`}>
                                    <Badge
                                        variant="secondary"
                                        className="text-xs capitalize hover:bg-hc-amber-light/15 hover:text-hc-amber-dim transition-colors cursor-pointer"
                                    >
                                        {effect.name}
                                    </Badge>
                                </Link>
                            ))}
                        </div>
                    )}

                    <Separator />

                    {product.variants.length > 1 && (
                        <div>
                            <p className="text-sm font-semibold mb-3">
                                {variant ? getVariantLabel(variant) : 'Select variant'}
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {product.variants.map((v: ProductVariant) => (
                                    <Button
                                        key={v.id} size="sm"
                                        variant={variant?.id === v.id ? 'default' : 'outline'}
                                        onClick={() => { setSelectedVariant(v); setActiveMedia(null) }}
                                    >
                                        {getVariantLabel(v)}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="flex items-center gap-4">
                        <span className="text-sm font-semibold">Quantity</span>
                        <div className="flex items-center rounded-md border overflow-hidden">
                            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-none"
                                    onClick={() => setQty(q => Math.max(1, q - 1))}
                                    disabled={qty <= 1}
                                    aria-label="Decrease quantity">
                                <Minus className="h-4 w-4" />
                            </Button>
                            <span className="px-4 text-sm font-semibold min-w-[40px] text-center tabular-nums">{qty}</span>
                            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-none"
                                    onClick={() => setQty(q => q + 1)}
                                    aria-label="Increase quantity">
                                <Plus className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                    <Button
                        size="lg" className="w-full"
                        onClick={() => variant && addToCart.mutate({ variant: variant.id, quantity: qty })}
                        disabled={!variant || addToCart.isPending}
                    >
                        <ShoppingBag className="h-5 w-5 mr-2" />
                        {addToCart.isPending ? 'Adding…' : 'Add to Cart'}
                    </Button>

                    {/* Product details — weight, subtype, potency, terpenes, COA.
                        Falls back to the generic attribute table only for
                        products that still carry old-style EAV attributes. */}
                    {variant && variant.attributes.length > 0 ? (
                        <Card className="divide-y overflow-hidden">
                            {variant.attributes.map((attr: Attribute) => (
                                <div key={attr.id} className="flex justify-between px-4 py-3 text-sm">
                                    <span className="text-muted-foreground">{attr.name}</span>
                                    <span className="font-medium">{attr.value}</span>
                                </div>
                            ))}
                        </Card>
                    ) : (
                        <ProductSpecs product={product} variant={variant} />
                    )}

                    <RelatedGuideLink product={product} />

                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { icon: Truck,       text: 'Free shipping $100+' },
                            { icon: RotateCcw,   text: '30-day returns'     },
                            { icon: ShieldCheck, text: 'Secure checkout'    },
                        ].map(({ icon: Icon, text }) => (
                            <div key={text} className="flex flex-col items-center gap-1.5 p-3 rounded-xl bg-muted text-center">
                                <Icon className="h-4 w-4 text-hc-amber-dim" />
                                <span className="text-xs text-muted-foreground">{text}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

// ── Related /learn guide link ─────────────────────────────────────────────
//
// Points to the single most relevant answer-content page for this product
// (edibles onset, indica/sativa/hybrid, COA reading, or dosing basics),
// picked from the product's own compliance_category/cannabis_type/lab data.

function RelatedGuideLink({ product }: { product: Product }) {
    const guide = getGuideForProduct(product)
    return (
        <Link
            href={`/learn/${guide.slug}`}
            className="flex items-center gap-2 rounded-xl bg-muted px-4 py-3 text-sm font-medium text-hc-ink hover:bg-muted/70 transition-colors"
        >
            <BookOpen className="h-4 w-4 shrink-0 text-hc-amber-dim" />
            <span className="truncate">{guide.title}</span>
            <ChevronRight className="h-4 w-4 shrink-0 ml-auto text-muted-foreground" />
        </Link>
    )
}

// ── Product specs / potency panel ─────────────────────────────────────────
//
// Replaces the old generic attribute table for products that now carry
// their weight/potency/terpene data in real columns instead of EAV
// Attribute rows. Renders nothing if there's genuinely nothing to show
// (e.g. an accessory with no weight, no lab, no subtype).

function ProductSpecs({ product, variant }: { product: Product; variant: ProductVariant | null }) {
    const lab = variant?.lab ?? null
    const weight = formatWeight(variant?.weight_value, variant?.weight_unit)

    const rows: { label: string; value: string }[] = []
    if (weight) rows.push({ label: 'Size', value: weight })
    if (product.sub_type) rows.push({ label: 'Form', value: product.sub_type })
    if (product.compliance_category) {
        rows.push({ label: 'Category', value: COMPLIANCE_CATEGORY_LABEL[product.compliance_category] })
    }

    const cannabinoidFields: [keyof NonNullable<typeof lab>, string][] = [
        ['thc_percent', 'THC'], ['thca_percent', 'THCa'],
        ['cbd_percent', 'CBD'], ['cbda_percent', 'CBDa'],
        ['cbn_percent', 'CBN'], ['cbg_percent', 'CBG'],
    ]
    if (lab) {
        for (const [field, label] of cannabinoidFields) {
            const value = lab[field]
            if (typeof value === 'string' && value) {
                rows.push({ label, value: `${parseFloat(value)}%` })
            }
        }
    }

    const terpenes = lab
        ? Object.entries(lab.terpenes?.terpenes ?? {})
            .filter(([, v]) => v?.value != null)
            .sort(([, a], [, b]) => (b.value ?? 0) - (a.value ?? 0))
            .slice(0, 6)
        : []

    const coaUrl = lab?.coa_url || null

    if (rows.length === 0 && terpenes.length === 0 && !coaUrl) return null

    return (
        <div className="space-y-3">
            {rows.length > 0 && (
                <Card className="divide-y overflow-hidden">
                    {rows.map(row => (
                        <div key={row.label} className="flex justify-between px-4 py-3 text-sm">
                            <span className="text-muted-foreground">{row.label}</span>
                            <span className="font-medium">{row.value}</span>
                        </div>
                    ))}
                </Card>
            )}

            {terpenes.length > 0 && (
                <div>
                    <p className="text-sm font-semibold mb-2">Terpene profile</p>
                    <div className="flex flex-wrap gap-1.5">
                        {terpenes.map(([name, data]) => (
                            <Badge key={name} variant="outline" className="text-xs">
                                {titleCase(name)}
                                {data.value != null && (
                                    <span className="text-muted-foreground ml-1">
                                        {data.value}{data.unit ?? ''}
                                    </span>
                                )}
                            </Badge>
                        ))}
                    </div>
                </div>
            )}

            {coaUrl && (
                <a
                    href={coaUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm font-medium text-hc-amber-dim hover:text-hc-amber transition-colors"
                >
                    <FileText className="h-4 w-4" />
                    View Certificate of Analysis
                </a>
            )}
        </div>
    )
}