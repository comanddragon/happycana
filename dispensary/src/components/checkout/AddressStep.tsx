'use client'

import { Check, Plus, MapPin } from 'lucide-react'
import { cn } from '@/lib/utils'
import { CheckoutSection } from './CheckoutSection'
import { NewAddressForm } from './NewAddressForm'
import type { Address } from './types'
import type { AddressForm as AddressFormValues } from '@/lib/checkout/schema'

interface AddressStepProps {
    addresses: Address[] | undefined
    selectedAddress: string
    onSelectAddress: (id: string) => void
    newAddrOpen: boolean
    onToggleNewAddr: () => void
    onSaveAddress: (data: AddressFormValues) => Promise<void>
    isSavingAddress: boolean
}

export function AddressStep({
    addresses,
    selectedAddress,
    onSelectAddress,
    newAddrOpen,
    onToggleNewAddr,
    onSaveAddress,
    isSavingAddress,
}: AddressStepProps) {
    return (
        <CheckoutSection index={1} title="Delivery Address" icon={MapPin}>
            {addresses && addresses.length > 0 && (
                <div className="mb-4 space-y-2.5">
                    {addresses.map(addr => (
                        <button
                            key={addr.id}
                            onClick={() => onSelectAddress(addr.id)}
                            className={cn(
                                'w-full rounded-xl border p-4 text-left transition-all duration-200',
                                selectedAddress === addr.id
                                    ? 'border-hc-amber bg-hc-amber-light/[0.08] ring-1 ring-hc-amber/30'
                                    : 'border-hc-ink/10 hover:border-hc-ink/25',
                            )}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div>
                                    <p className="text-sm font-medium text-hc-ink">{addr.line1}</p>
                                    {addr.line2 && <p className="text-xs text-hc-ink-soft">{addr.line2}</p>}
                                    <p className="text-xs text-hc-ink-soft">
                                        {addr.city}, {addr.state} {addr.postal_code}, {addr.country}
                                    </p>
                                </div>
                                <span className={cn(
                                    'flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition-colors',
                                    selectedAddress === addr.id ? 'border-hc-amber bg-hc-amber text-hc-canopy-2' : 'border-hc-ink/15',
                                )}>
                                    {selectedAddress === addr.id && <Check className="h-3 w-3" />}
                                </span>
                            </div>
                            {addr.is_default && (
                                <span className="mt-2 inline-block rounded-full bg-hc-paper-2 px-2 py-0.5 font-hc-mono text-[10px] uppercase tracking-wide text-hc-ink-soft">
                                    Default
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            )}

            <button
                onClick={onToggleNewAddr}
                className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-dashed border-hc-ink/20 py-3 text-sm font-medium text-hc-ink-soft transition-colors hover:border-hc-amber hover:text-hc-amber-dim"
            >
                <Plus className="h-3.5 w-3.5" /> Add new address
            </button>

            <NewAddressForm open={newAddrOpen} onSubmit={onSaveAddress} isSubmitting={isSavingAddress} />
        </CheckoutSection>
    )
}
