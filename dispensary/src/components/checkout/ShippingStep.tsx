'use client'

import { Check, Truck } from 'lucide-react'
import { cn, formatPrice } from '@/lib/utils'
import { CheckoutSection } from './CheckoutSection'
import type { ShippingMethod } from './types'

interface ShippingStepProps {
    methods: ShippingMethod[] | undefined
    selectedShipping: string
    onSelect: (id: string) => void
    locked: boolean
}

export function ShippingStep({ methods, selectedShipping, onSelect, locked }: ShippingStepProps) {
    return (
        <CheckoutSection
            index={2}
            title="Shipping Method"
            icon={Truck}
            locked={locked}
            lockedHint="Select a delivery address to continue"
        >
            {!methods?.length && (
                <p className="text-sm text-hc-ink-soft">No shipping methods available.</p>
            )}
            <div className="space-y-2.5">
                {methods?.map(method => (
                    <button
                        key={method.id}
                        onClick={() => onSelect(method.id)}
                        className={cn(
                            'w-full rounded-xl border p-4 text-left transition-all duration-200',
                            selectedShipping === method.id
                                ? 'border-hc-amber bg-hc-amber-light/[0.08] ring-1 ring-hc-amber/30'
                                : 'border-hc-ink/10 hover:border-hc-ink/25',
                        )}
                    >
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <p className="text-sm font-medium text-hc-ink">{method.name}</p>
                                <p className="text-xs text-hc-ink-soft">
                                    {method.carrier} · {method.estimated_days_min}–{method.estimated_days_max} business days
                                </p>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="font-hc-mono text-sm font-medium text-hc-ink">{formatPrice(method.price)}</span>
                                <span className={cn(
                                    'flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors',
                                    selectedShipping === method.id ? 'border-hc-amber bg-hc-amber text-hc-canopy-2' : 'border-hc-ink/15',
                                )}>
                                    {selectedShipping === method.id && <Check className="h-3 w-3" />}
                                </span>
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </CheckoutSection>
    )
}
