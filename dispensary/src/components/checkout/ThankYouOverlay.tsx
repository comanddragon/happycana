'use client'

import { useState } from 'react'
import { PartyPopper, Copy, Check, Sparkle } from 'lucide-react'
import { AMBER_GRADIENT } from '@/lib/checkout/constants'

interface ThankYouOverlayProps {
    orderId: string
    onContinue: () => void
}

export function ThankYouOverlay({ orderId, onContinue }: ThankYouOverlayProps) {
    const [copied, setCopied] = useState(false)
    const [copyCount, setCopyCount] = useState(0)
    const shortId = orderId.slice(0, 8).toUpperCase()

    async function handleCopy() {
        const frontendName = process.env.NEXT_PUBLIC_FRONTEND_NAME
        await navigator.clipboard.writeText(`${frontendName} - ${shortId}`)
        setCopied(true)
        setCopyCount(c => c + 1)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-hc-ink/60 px-4 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="relative w-full max-w-md rounded-3xl bg-white p-8 text-center shadow-2xl animate-in zoom-in-95 slide-in-from-bottom-4 duration-300">
                <div
                    className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full text-hc-canopy-2"
                    style={AMBER_GRADIENT}
                >
                    <PartyPopper className="h-8 w-8" />
                </div>
                <h2 className="font-hc-display text-2xl font-medium text-hc-ink">Thank you so much! 🎉</h2>
                <p className="mt-3 text-sm leading-relaxed text-hc-ink-soft">
                    Your order{' '}
                    <span className="font-hc-mono font-medium text-hc-ink">
                        #{shortId}
                    </span>{' '}
                    has landed safely with us. We&apos;ll be in touch <em>very</em> soon to confirm the details
                    and sort out payment — sit tight, good things are on the way!
                </p>
                <p className="mt-2 text-xs text-red-600">
                    Copy your order number and paste in the chat at the bottom right of your screen
                </p>
                <div className="relative inline-block">
                    <button
                        type="button"
                        onClick={handleCopy}
                        className={`mt-2 inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all duration-300 ${
                            copied
                                ? 'bg-emerald-50 text-emerald-600 shadow-[0_0_0_3px_rgba(16,185,129,0.35),0_0_16px_rgba(16,185,129,0.55)]'
                                : 'bg-hc-ink/5 text-hc-ink-soft hover:bg-hc-ink/10'
                        }`}
                    >
                        {copied ? (
                            <>
                                <Check className="h-3.5 w-3.5" />
                                Copied
                            </>
                        ) : (
                            <>
                                <Copy className="h-3.5 w-3.5" />
                                Copy Order Number
                            </>
                        )}
                    </button>

                    {copied && (
                        <span key={copyCount} className="pointer-events-none absolute inset-0">
                            <Sparkle className="absolute -left-2 -top-3 h-3 w-3 fill-emerald-400 text-emerald-400 animate-in zoom-in fade-out spin-in-45 duration-700" />
                            <Sparkle className="absolute -right-3 -top-1 h-2.5 w-2.5 fill-emerald-400 text-emerald-400 animate-in zoom-in fade-out spin-in-90 duration-700 delay-75" />
                            <Sparkle className="absolute -bottom-2 left-1/3 h-2 w-2 fill-emerald-400 text-emerald-400 animate-in zoom-in fade-out spin-in-12 duration-700 delay-150" />
                        </span>
                    )}
                </div>
                <button
                    onClick={onContinue}
                    className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full py-3 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5"
                    style={AMBER_GRADIENT}
                >
                    Continue
                </button>
            </div>
        </div>
    )
}