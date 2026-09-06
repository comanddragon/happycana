'use client'

import { CreditCard, ShieldCheck, Wallet } from 'lucide-react'
import { cn } from '@/lib/utils'
import { CheckoutSection } from './CheckoutSection'
import type { Gateway } from './types'

interface PaymentStepProps {
    gateway: Gateway
    onSelect: (gateway: Gateway) => void
    locked: boolean
}

export function PaymentStep({ gateway, onSelect, locked }: PaymentStepProps) {
    return (
        <CheckoutSection
            index={3}
            title="Payment Method"
            icon={Wallet}
            locked={locked}
            lockedHint="Choose a shipping method to continue"
        >
            <div className="grid grid-cols-2 gap-3">
                {(['stripe', 'paypal'] as const).map(gw => (
                    <button
                        key={gw}
                        onClick={() => onSelect(gw)}
                        className={cn(
                            'flex items-center justify-center gap-2 rounded-xl border p-4 text-sm font-medium capitalize transition-all duration-200',
                            gateway === gw
                                ? 'border-hc-amber bg-hc-amber-light/[0.08] text-hc-amber-dim ring-1 ring-hc-amber/30'
                                : 'border-hc-ink/10 text-hc-ink-soft hover:border-hc-ink/25',
                        )}
                    >
                        <CreditCard className="h-4 w-4" />
                        {gw === 'stripe' ? 'Credit Card' : 'PayPal'}
                    </button>
                ))}
            </div>
            <p className="mt-3.5 flex items-center gap-1.5 text-xs text-hc-ink-soft">
                <ShieldCheck className="h-3.5 w-3.5 text-hc-sage-dim" />
                Your payment info is handled securely by {gateway === 'stripe' ? 'Stripe' : 'PayPal'}.
            </p>
        </CheckoutSection>
    )
}
