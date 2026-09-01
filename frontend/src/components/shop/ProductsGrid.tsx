'use client'

import { useCallback, useMemo, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Search, X, SearchX, SlidersHorizontal } from 'lucide-react'
import { useProducts, useCategories, useBrands, useEffects } from '@/hooks/useApi'
import { ProductCard } from '@/components/shop/ProductCard'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter } from '@/components/ui/sheet'
import { CANNABIS_TYPE_LABEL, THC_PRESETS } from '@/lib/utils'
import type { CannabisType } from '@/types'

const SORT_OPTIONS = [
    { label: 'Newest',      value: '-created_at' },
    { label: 'Oldest',      value: 'created_at'  },
    { label: 'Price: Low',  value: 'base_price'  },
    { label: 'Price: High', value: '-base_price' },
    { label: 'Name A-Z',    value: 'name'        },
]

const ALL_CATEGORIES = '__all__'
const ALL_BRANDS      = '__all__'
const ALL_TYPES        = '__all__'
const CANNABIS_TYPES: CannabisType[] = ['sativa', 'indica', 'hybrid', 'hybrid_sativa', 'hybrid_indica']

interface Props {
    initialCategory?: string
    initialOrdering?: string
    initialSearch?: string
    initialPage?: number
    /** Route filter/sort/pagination changes push to. Lets landing pages like
     *  /shop/new-arrivals or /shop/best-sellers reuse this grid without
     *  navigating the user away to /shop/products on the first interaction. */
    basePath?: string
}

export function ProductsGrid({
    initialCategory = '',
    initialOrdering = '-created_at',
    initialSearch = '',
    initialPage = 1,
    basePath = '/shop/products',
}: Props) {
    const router       = useRouter()
    const searchParams = useSearchParams()

    const category    = searchParams.get('category') ?? initialCategory
    const ordering     = searchParams.get('ordering') ?? initialOrdering
    const search        = searchParams.get('search')   ?? initialSearch
    const brand          = searchParams.get('brand') ?? ''
    const cannabisType    = searchParams.get('cannabis_type') ?? ''
    const effect            = searchParams.get('effect') ?? ''
    const minThc              = searchParams.get('min_thc') ?? ''
    const inStock               = searchParams.get('in_stock') === 'true'
    const page                    = Number(searchParams.get('page') ?? initialPage)

    const [searchDraft, setSearchDraft] = useState(search)
    const [filtersOpen, setFiltersOpen] = useState(false)

    const { data, isLoading, isFetching } = useProducts({
        ...(category && { category }),
        ...(brand && { brand }),
        ...(cannabisType && { cannabis_type: cannabisType }),
        ...(effect && { effect }),
        ...(minThc && { min_thc: Number(minThc) }),
        ...(inStock && { in_stock: true }),
        ordering,
        ...(search && { search }),
        page,
    })

    const { data: categories } = useCategories()
    const { data: brands }       = useBrands()
    const { data: effects }        = useEffects()

    const setParam = useCallback((key: string, value: string) => {
        const p = new URLSearchParams(searchParams.toString());
        if (value) {
            p.set(key, value);
        } else {
            p.delete(key);
        }
        // Reset to page 1 only when changing filters
        if (key !== "page") {
            p.delete("page");
        }
        router.push(`${basePath}?${p.toString()}`);
    }, [searchParams, router, basePath]);

    const setParams = useCallback((updates: Record<string, string>) => {
        const p = new URLSearchParams(searchParams.toString())
        for (const [key, value] of Object.entries(updates)) {
            if (value) p.set(key, value)
            else p.delete(key)
        }
        p.delete('page')
        router.push(`${basePath}?${p.toString()}`)
    }, [searchParams, router, basePath])

    const clearFilters = () => {
        setSearchDraft('')
        router.push(basePath)
    }

    const clearAdvancedFilters = () => {
        setParams({ brand: '', cannabis_type: '', effect: '', min_thc: '', in_stock: '' })
    }

    const hasFilters = Boolean(category || search || brand || cannabisType || effect || minThc || inStock)
    const advancedFilterCount = [brand, cannabisType, effect, minThc, inStock ? '1' : ''].filter(Boolean).length

    const selectedThcPreset = useMemo(
        () => THC_PRESETS.find(p => String(p.min_thc ?? '') === minThc) ?? THC_PRESETS[0],
        [minThc],
    )

    return (
        <>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
                <div className="flex items-center gap-2 flex-wrap">
                    <div className="relative">
                        <Search className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-hc-ink-soft/50" />
                        <Input
                            type="text"
                            placeholder="Search products…"
                            value={searchDraft}
                            onChange={e => setSearchDraft(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') setParam('search', searchDraft) }}
                            className="w-48 pl-8"
                        />
                    </div>

                    <Select
                        value={category || ALL_CATEGORIES}
                        onValueChange={val => setParam('category', val === ALL_CATEGORIES ? '' : val)}
                    >
                        <SelectTrigger className="w-auto min-w-[9rem]">
                            <SelectValue placeholder="All Categories" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value={ALL_CATEGORIES}>All Categories</SelectItem>
                            {categories?.map(cat => (
                                <SelectItem key={cat.id} value={cat.slug}>{cat.name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setFiltersOpen(true)}
                        className="gap-1.5"
                    >
                        <SlidersHorizontal className="h-3.5 w-3.5" />
                        Filters
                        {advancedFilterCount > 0 && (
                            <Badge variant="secondary" className="ml-0.5 h-5 min-w-5 justify-center px-1">
                                {advancedFilterCount}
                            </Badge>
                        )}
                    </Button>

                    {hasFilters ? (
                        <Button variant="ghost" size="sm" onClick={clearFilters} className="gap-1.5 text-red-600 hover:text-red-700 hover:bg-red-50">
                            <X className="h-3.5 w-3.5" /> Clear
                        </Button>
                    ) : null}
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-sm text-hc-ink-soft hidden sm:block">Sort:</span>
                    <Select value={ordering} onValueChange={val => setParam('ordering', val)}>
                        <SelectTrigger className="w-auto min-w-[9rem]">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {SORT_OPTIONS.map(o => (
                                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {(brand || cannabisType || effect || minThc || inStock) && (
                <div className="flex flex-wrap items-center gap-1.5 mb-6 -mt-2">
                    {brand && (
                        <Badge variant="outline" className="gap-1">
                            {brands?.find(b => b.slug === brand)?.name ?? brand}
                            <button onClick={() => setParam('brand', '')} aria-label="Remove brand filter">
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    )}
                    {cannabisType && (
                        <Badge variant="outline" className="gap-1">
                            {CANNABIS_TYPE_LABEL[cannabisType]}
                            <button onClick={() => setParam('cannabis_type', '')} aria-label="Remove strain type filter">
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    )}
                    {effect && (
                        <Badge variant="outline" className="gap-1 capitalize">
                            {effect}
                            <button onClick={() => setParam('effect', '')} aria-label="Remove effect filter">
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    )}
                    {minThc && (
                        <Badge variant="outline" className="gap-1">
                            {minThc}%+ THC
                            <button onClick={() => setParam('min_thc', '')} aria-label="Remove potency filter">
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    )}
                    {inStock && (
                        <Badge variant="outline" className="gap-1">
                            In stock
                            <button onClick={() => setParam('in_stock', '')} aria-label="Remove in-stock filter">
                                <X className="h-3 w-3" />
                            </button>
                        </Badge>
                    )}
                </div>
            )}

            {/* Pagination (top) */}
            {data && data.count > 20 ? (
                <div className="flex items-center justify-center gap-2 mb-4 z-100">
                    {data.previous ? (
                        <Button variant="outline" size="sm" onClick={() => setParam('page', String(page - 1))}>
                            Previous
                        </Button>
                    ) : null}
                    <span className="text-sm text-hc-ink-soft">
            Page {page} of {Math.ceil(data.count / 20)}
          </span>
                    {data.next ? (
                        <Button size="sm" onClick={() => setParam('page', String(page + 1))}>
                            Next
                        </Button>
                    ) : null}
                </div>
            ) : null}

            {isLoading ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                    {Array.from({ length: 12 }).map((_, i) => (
                        <div key={i} className="space-y-3 animate-pulse">
                            <div className="aspect-square skeleton rounded-2xl" />
                            <div className="h-4 skeleton rounded w-3/4" />
                            <div className="h-4 skeleton rounded w-1/2" />
                        </div>
                    ))}
                </div>
            ) : data?.results.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <div className="h-14 w-14 rounded-2xl bg-hc-paper-2 flex items-center justify-center mb-4">
                        <SearchX className="h-6 w-6 text-hc-ink-soft/50" />
                    </div>
                    <h2 className="font-hc-display text-xl font-medium text-hc-ink">No products found</h2>
                    <p className="text-hc-ink-soft mt-1 text-sm">Try adjusting your filters</p>
                    <Button size="sm" onClick={clearFilters} className="mt-4">Clear filters</Button>
                </div>
            ) : (
                <div
                    className={`grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5 transition-opacity duration-150 ${isFetching ? 'opacity-60' : 'opacity-100'}`}
                >
                    {data?.results.map((product, i) => (
                        <ProductCard key={product.id} product={product} priority={i < 4} />
                    ))}
                </div>
            )}

            {/* Pagination (bottom) */}
            {data && data.count > 20 ? (
                <div className="flex items-center justify-center gap-2 mt-12 z-100">
                    {data.previous ? (
                        <Button variant="outline" size="sm" onClick={() => setParam('page', String(page - 1))}>
                            Previous
                        </Button>
                    ) : null}
                    <span className="text-sm text-hc-ink-soft">
            Page {page} of {Math.ceil(data.count / 20)}
          </span>
                    {data.next ? (
                        <Button size="sm" onClick={() => setParam('page', String(page + 1))}>
                            Next
                        </Button>
                    ) : null}
                </div>
            ) : null}

            <Sheet open={filtersOpen} onOpenChange={setFiltersOpen}>
                <SheetContent side="right" className="w-full sm:max-w-sm overflow-y-auto">
                    <SheetHeader>
                        <SheetTitle>Filters</SheetTitle>
                        <SheetDescription>Narrow down by brand, strain type, effect, and potency.</SheetDescription>
                    </SheetHeader>

                    <div className="flex flex-col gap-6 px-4">
                        <div className="space-y-2">
                            <Label>Brand</Label>
                            <Select
                                value={brand || ALL_BRANDS}
                                onValueChange={val => setParam('brand', val === ALL_BRANDS ? '' : val)}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="All Brands" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value={ALL_BRANDS}>All Brands</SelectItem>
                                    {brands?.map(b => (
                                        <SelectItem key={b.id} value={b.slug}>{b.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Strain type</Label>
                            <Select
                                value={cannabisType || ALL_TYPES}
                                onValueChange={val => setParam('cannabis_type', val === ALL_TYPES ? '' : val)}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Any strain type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value={ALL_TYPES}>Any strain type</SelectItem>
                                    {CANNABIS_TYPES.map(t => (
                                        <SelectItem key={t} value={t}>{CANNABIS_TYPE_LABEL[t]}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Potency</Label>
                            <Select
                                value={selectedThcPreset.label}
                                onValueChange={label => {
                                    const preset = THC_PRESETS.find(p => p.label === label)
                                    setParam('min_thc', preset?.min_thc ? String(preset.min_thc) : '')
                                }}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {THC_PRESETS.map(p => (
                                        <SelectItem key={p.label} value={p.label}>{p.label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {effects && effects.length > 0 && (
                            <div className="space-y-2">
                                <Label>Effect</Label>
                                <div className="flex flex-wrap gap-1.5">
                                    {effects.map(e => (
                                        <button
                                            key={e.id}
                                            onClick={() => setParam('effect', effect === e.slug ? '' : e.slug)}
                                            className="focus-visible:outline-none"
                                        >
                                            <Badge
                                                variant={effect === e.slug ? 'default' : 'outline'}
                                                className="cursor-pointer capitalize text-xs"
                                            >
                                                {e.name}
                                            </Badge>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        <Separator />

                        <div className="flex items-center gap-2">
                            <Checkbox
                                id="in-stock"
                                checked={inStock}
                                onCheckedChange={checked => setParam('in_stock', checked ? 'true' : '')}
                            />
                            <Label htmlFor="in-stock" className="text-sm font-normal cursor-pointer">
                                In stock only
                            </Label>
                        </div>
                    </div>

                    <SheetFooter>
                        <Button variant="outline" onClick={clearAdvancedFilters} disabled={advancedFilterCount === 0}>
                            Clear filters
                        </Button>
                        <Button onClick={() => setFiltersOpen(false)}>Show results</Button>
                    </SheetFooter>
                </SheetContent>
            </Sheet>
        </>
    )
}