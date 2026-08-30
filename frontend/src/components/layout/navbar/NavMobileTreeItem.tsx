'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown } from 'lucide-react'
import type { MenuNode } from '@/components/layout/navbar/NavFlyoutItem'

export function NavMobileTreeItem({
    node,
    depth = 0,
    onNavigateAction,
}: {
    node: MenuNode
    depth?: number
    onNavigateAction: () => void
}) {
    const [open, setOpen] = useState(false)
    const hasChildren = !!node.children?.length

    if (!hasChildren) {
        return (
            <Link
                href={node.href ?? '#'}
                onClick={onNavigateAction}
                className="block rounded-lg px-3 py-2 text-sm text-hc-sage transition-colors hover:bg-hc-paper/5 hover:text-hc-paper"
            >
                {node.label}
            </Link>
        )
    }

    return (
        <div>
            <button
                onClick={() => setOpen(o => !o)}
                className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm text-hc-sage transition-colors hover:bg-hc-paper/5 hover:text-hc-paper"
            >
                {node.href ? (
                    <Link href={node.href} onClick={onNavigateAction} className="flex-1 text-left">
                        {node.label}
                    </Link>
                ) : (
                    <span className="flex-1 text-left">{node.label}</span>
                )}
                <ChevronDown className={`h-4 w-4 transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>

            {open && (
                <div className="ml-4 mt-1 space-y-1 border-l border-hc-paper/10 pl-3">
                    {node.children!.map((child, i) => (
                        <NavMobileTreeItem
                            key={`${child.label}-${child.href ?? i}`}
                            node={child}
                            depth={depth + 1}
                            onNavigateAction={onNavigateAction}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
