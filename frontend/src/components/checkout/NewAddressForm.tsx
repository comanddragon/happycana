'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { addressSchema, type AddressForm as AddressFormValues } from '@/lib/checkout/schema'
import { AMBER_GRADIENT } from '@/lib/checkout/constants'

const FIELDS = [
    ['line1', 'Street address'],
    ['line2', 'Apartment, suite, etc. (optional)'],
    ['city', 'City'],
    ['state', 'State'],
    ['postal_code', 'ZIP / Postal code'],
    ['country', 'Country'],
] as const

interface NewAddressFormProps {
    open: boolean
    onSubmit: (data: AddressFormValues) => Promise<void>
    isSubmitting: boolean
}

export function NewAddressForm({ open, onSubmit, isSubmitting }: NewAddressFormProps) {
    const form = useForm<AddressFormValues>({ resolver: zodResolver(addressSchema) })

    const submit = form.handleSubmit(async data => {
        await onSubmit(data)
        form.reset()
    })

    return (
        // Pure-CSS accordion: grid-rows trick avoids a JS height measurement
        <div className={cn(
            'grid transition-[grid-template-rows] duration-300 ease-out',
            open ? 'grid-rows-[1fr] mt-4' : 'grid-rows-[0fr]',
        )}>
            <div className="overflow-hidden">
                <form onSubmit={submit} className="space-y-3 border-t border-hc-ink/10 pt-4">
                    {FIELDS.map(([field, placeholder]) => (
                        <div key={field}>
                            <input
                                {...form.register(field)}
                                placeholder={placeholder}
                                className="w-full rounded-lg border border-hc-ink/15 bg-hc-paper px-3.5 py-2.5 text-sm text-hc-ink placeholder:text-hc-ink-soft/60 outline-none transition-colors focus:border-hc-amber focus:ring-2 focus:ring-hc-amber/15"
                            />
                            {form.formState.errors[field] && (
                                <p className="mt-1 text-xs text-red-500">
                                    {form.formState.errors[field]?.message}
                                </p>
                            )}
                        </div>
                    ))}
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-semibold text-hc-canopy-2 transition-transform hover:-translate-y-0.5 disabled:opacity-60 disabled:hover:translate-y-0"
                        style={AMBER_GRADIENT}
                    >
                        {isSubmitting && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                        {isSubmitting ? 'Saving…' : 'Save Address'}
                    </button>
                </form>
            </div>
        </div>
    )
}
