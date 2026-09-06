'use client'

import { Mail, ShieldCheck } from 'lucide-react'
import { CheckoutSection } from './CheckoutSection'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface ContactStepProps {
    isGuest: boolean
    knownEmail?: string
    email: string
    onEmailChange: (value: string) => void
    locked: boolean
}

export function ContactStep({ isGuest, knownEmail, email, onEmailChange, locked }: ContactStepProps) {
    return (
        <CheckoutSection
            index={4}
            title="Contact"
            icon={Mail}
            locked={locked}
            lockedHint="Choose a shipping method to continue"
        >
            {isGuest ? (
                <div className="space-y-1.5">
                    <Label htmlFor="contact-email">
                        Email <span className="text-destructive">*</span>
                    </Label>
                    <Input
                        id="contact-email"
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={e => onEmailChange(e.target.value)}
                    />
                    <p className="text-xs text-hc-ink-soft">
                        So we know where to reach you about your order.
                    </p>
                </div>
            ) : (
                <p className="text-sm text-hc-ink-soft">
                    We&apos;ll reach you at <span className="font-medium text-hc-ink">{knownEmail}</span>.
                </p>
            )}
            <p className="mt-3.5 flex items-center gap-1.5 text-xs text-hc-ink-soft">
                <ShieldCheck className="h-3.5 w-3.5 text-hc-sage-dim" />
                Your selected payment method will be included with your order confirmation.
            </p>
        </CheckoutSection>
    )
}
