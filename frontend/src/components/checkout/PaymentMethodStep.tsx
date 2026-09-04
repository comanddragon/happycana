'use client'

import Image from 'next/image'
import { CreditCard } from 'lucide-react'
import { CheckoutSection } from './CheckoutSection'
import { cn } from '@/lib/utils'
import type { PaymentMethod } from '@/types'

interface PaymentMethodStepProps {
    methods?: PaymentMethod[]
    selectedMethod: number | null
    onSelect: (id: number) => void
    locked: boolean
}

export function PaymentMethodStep({ methods, selectedMethod, onSelect, locked }: PaymentMethodStepProps) {
    return (
        <CheckoutSection
            index={3}
            title="Payment Method"
            icon={CreditCard}
            locked={locked}
            lockedHint="Choose a shipping method to continue"
        >
            <div className="grid gap-3">
                {methods?.map(method => {
                    const selected = method.id === selectedMethod
                    return (
                        <button
                            key={method.id}
                            type="button"
                            onClick={() => onSelect(method.id)}
                            className={cn(
                                'flex items-center gap-4 rounded-xl border p-4 text-left transition-colors',
                                selected
                                    ? 'border-hc-amber bg-hc-amber/5 ring-1 ring-hc-amber/30'
                                    : 'border-hc-ink/10 hover:border-hc-ink/25',
                            )}
                        >
                            <span className="flex h-12 w-28 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white">
                                <Image src={method.logo_url} alt={method.name} width={112} height={48} className="h-full w-full object-contain" />
                            </span>
                            <span className="min-w-0 flex-1">
                                <span className="block text-sm font-semibold text-hc-ink">{method.name}</span>
                                <span className="mt-1 block text-xs leading-relaxed text-hc-ink-soft">{method.description}</span>
                            </span>
                            <span className={cn('h-4 w-4 shrink-0 rounded-full border-2', selected ? 'border-[5px] border-hc-amber' : 'border-hc-ink/25')} />
                        </button>
                    )
                })}
            </div>
        </CheckoutSection>
    )
}
