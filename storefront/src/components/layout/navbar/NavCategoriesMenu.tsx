'use client'

import { ChevronDown } from 'lucide-react'
import { useCategoriesMenuTree } from '@/hooks/useCategoriesMenuTree'
import { NavFlyoutItem } from '@/components/layout/navbar/NavFlyoutItem'
import { useStorefront } from '@/storefront/StorefrontProvider'

export function NavCategoriesMenu() {
    const { storefront, features } = useStorefront()
    const { rootNodes } = useCategoriesMenuTree({ includeEffects: storefront.kind !== 'dispensary' })

    return (
        <div className="group relative">
            <button
                className="flex items-center gap-1 text-sm font-medium text-hc-sage transition-colors hover:text-hc-paper"
            >
                {storefront.kind === 'hash' ? 'Hash styles' : features.peptideCatalog ? 'Research areas' : 'Categories'}
                <ChevronDown className="h-4 w-4 transition-transform duration-200 group-hover:rotate-180 group-focus-within:rotate-180" />
            </button>

            <div className="pointer-events-none invisible absolute left-0 top-full z-50 min-w-[220px] translate-y-1 pt-2 opacity-0 transition-[opacity,transform] duration-150 ease-out group-hover:pointer-events-auto group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100">
                <div className="rounded-xl border border-white/10 bg-hc-canopy-2 p-2 shadow-[0_16px_40px_rgba(0,0,0,.32)]">
                {rootNodes.length > 0 ? (
                    rootNodes.map((node, i) => (
                        <NavFlyoutItem key={`${node.label}-${i}`} node={node} />
                    ))
                ) : (
                    <div className="px-4 py-2 text-sm text-hc-sage/60">Loading…</div>
                )}
                </div>
            </div>
        </div>
    )
}
