import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AMBER_GRADIENT } from '@/lib/checkout/constants'

interface StepRailProps {
    addressDone: boolean
    shippingDone: boolean
    paymentDone: boolean
    contactDone: boolean
}

export function StepRail({ addressDone, shippingDone, paymentDone, contactDone }: StepRailProps) {
    const steps = [
        { label: 'Address',  done: addressDone },
        { label: 'Shipping', done: shippingDone },
        { label: 'Payment',  done: paymentDone },
        { label: 'Contact',  done: contactDone },
        { label: 'Review',   done: false },
    ]
    return (
        <ol className="flex items-center gap-2 sm:gap-3">
            {steps.map((step, i) => {
                const active = !step.done && (i === 0 || steps[i - 1].done)
                return (
                    <li key={step.label} className="flex items-center gap-2 sm:gap-3">
                        <div className="flex items-center gap-2">
                            <span
                                className={cn(
                                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-hc-mono text-[11px] transition-colors duration-300',
                                    step.done
                                        ? 'text-hc-canopy-2'
                                        : active
                                            ? 'border border-hc-amber text-hc-amber-dim'
                                            : 'border border-hc-ink/15 text-hc-ink-soft/60',
                                )}
                                style={step.done ? AMBER_GRADIENT : undefined}
                            >
                                {step.done ? <Check className="h-3.5 w-3.5" /> : i + 1}
                            </span>
                            <span className={cn(
                                'hidden font-hc-mono text-[11px] uppercase tracking-wide sm:inline',
                                step.done || active ? 'text-hc-ink' : 'text-hc-ink-soft/60',
                            )}>
                                {step.label}
                            </span>
                        </div>
                        {i < steps.length - 1 && (
                            <span className={cn(
                                'h-px w-5 sm:w-10 transition-colors duration-500',
                                step.done ? 'bg-hc-amber' : 'bg-hc-ink/10',
                            )} />
                        )}
                    </li>
                )
            })}
        </ol>
    )
}
