import { cn } from '@/lib/utils'
import React from "react";

interface CheckoutSectionProps {
    index: number
    title: string
    icon: React.ComponentType<{ className?: string }>
    locked?: boolean
    lockedHint?: string
    children: React.ReactNode
}

export function CheckoutSection({ index, title, icon: Icon, locked, lockedHint, children }: CheckoutSectionProps) {
    return (
        <div className={cn('relative rounded-2xl border bg-white p-6 transition-all duration-300', locked ? 'border-hc-ink/[0.06]' : 'border-hc-ink/[0.08]')}>
            <div className="mb-5 flex items-center gap-3">
                <span className={cn(
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-full font-hc-mono text-sm transition-colors',
                    locked ? 'bg-hc-paper-2 text-hc-ink-soft/50' : 'bg-hc-canopy text-hc-sage',
                )}>
                    {index}
                </span>
                <div className="flex items-center gap-2">
                    <Icon className={cn('h-4 w-4', locked ? 'text-hc-ink-soft/40' : 'text-hc-amber-dim')} />
                    <h2 className={cn('font-hc-display text-lg font-medium', locked ? 'text-hc-ink-soft/50' : 'text-hc-ink')}>
                        {title}
                    </h2>
                </div>
            </div>

            <div className={cn('transition-opacity duration-300', locked && 'pointer-events-none select-none opacity-40')}>
                {children}
            </div>

            {locked && lockedHint && (
                <p className="mt-4 font-hc-mono text-[11px] uppercase tracking-wide text-hc-ink-soft/50">
                    {lockedHint}
                </p>
            )}
        </div>
    )
}
