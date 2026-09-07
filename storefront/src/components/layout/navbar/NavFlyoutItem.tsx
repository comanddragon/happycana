'use client'

import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface MenuNode {
    label: string
    href?: string
    children?: MenuNode[]
}

export function NavFlyoutItem({ node }: { node: MenuNode }) {
    const hasChildren = !!node.children?.length

    const rowClasses = cn(
        'flex items-center gap-2 rounded-lg px-4 py-2 text-sm text-hc-sage transition-colors',
        'hover:bg-white/5 hover:text-hc-paper',
    )

    return (
        <div className="group/item relative after:absolute after:inset-y-0 after:left-full after:w-2">
            {node.href ? (
                <Link href={node.href} className={cn(rowClasses, 'justify-between')}>
                    <span className="truncate">{node.label}</span>
                    {hasChildren && <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-60" />}
                </Link>
            ) : (
                <div className={cn(rowClasses, 'justify-between cursor-default')}>
                    <span className="truncate">{node.label}</span>
                    {hasChildren && <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-60" />}
                </div>
            )}

            {hasChildren && (
                <div
                    className="pointer-events-none invisible absolute left-[calc(100%+0.5rem)] top-0 z-50 max-h-[360px] min-w-[200px] translate-x-1 overflow-y-auto rounded-xl border border-white/10 bg-hc-canopy-2 p-2 opacity-0 shadow-[0_16px_40px_rgba(0,0,0,.32)] transition-[opacity,transform] duration-150 ease-out group-hover/item:pointer-events-auto group-hover/item:visible group-hover/item:translate-x-0 group-hover/item:opacity-100 group-focus-within/item:pointer-events-auto group-focus-within/item:visible group-focus-within/item:translate-x-0 group-focus-within/item:opacity-100"
                >
                    {node.children!.map((child, i) => (
                        <NavFlyoutItem key={`${child.label}-${child.href ?? i}`} node={child} />
                    ))}
                </div>
            )}
        </div>
    )
}
