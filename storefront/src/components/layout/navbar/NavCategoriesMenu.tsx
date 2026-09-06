'use client'

import { ChevronDown } from 'lucide-react'
import { useCategoriesMenuTree } from '@/hooks/useCategoriesMenuTree'
import { NavFlyoutItem } from '@/components/layout/navbar/NavFlyoutItem'

export function NavCategoriesMenu() {
    const { rootNodes } = useCategoriesMenuTree()

    return (
        <div className="relative group">
            <button
                className="flex items-center gap-1 text-sm font-medium text-hc-sage transition-colors hover:text-hc-paper"
            >
                Categories
                <ChevronDown className="h-4 w-4 transition-transform group-hover:rotate-180" />
            </button>

            <div className="absolute left-0 top-full z-50 pt-2 hidden min-w-[220px] rounded-xl border border-white/10 bg-hc-canopy-2 p-2 shadow-xl group-hover:block">
                {rootNodes.length > 0 ? (
                    rootNodes.map((node, i) => (
                        <NavFlyoutItem key={`${node.label}-${i}`} node={node} />
                    ))
                ) : (
                    <div className="px-4 py-2 text-sm text-hc-sage/60">Loading…</div>
                )}
            </div>
        </div>
    )
}
