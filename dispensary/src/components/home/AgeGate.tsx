'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

const STORAGE_KEY = 'hc_age_ok'

export function AgeGate() {
    // Always render nothing until we've explicitly checked localStorage on
    // the client. This avoids relying on useSyncExternalStore's automatic
    // post-hydration re-check, which wasn't reliably re-syncing in this
    // setup — an explicit effect is slightly less elegant but leaves no
    // room for ambiguity about when the check actually runs.
    //
    // `mounted` and `alreadyVerified` are read from localStorage, which is
    // only available on the client, so they can't be computed during the
    // initial (server) render — hence the one-time effect below. They're
    // combined into a single state object so the effect only performs one
    // setState call instead of two.
    const [status, setStatus] = useState({ mounted: false, alreadyVerified: false })
    const [closing, setClosing] = useState(false)
    const [blocked, setBlocked] = useState(false)
    const [dismissed, setDismissed] = useState(false)
    const router = useRouter()

    useEffect(() => {
        let alreadyVerified = false
        try {
            alreadyVerified = localStorage.getItem(STORAGE_KEY) === '1'
        } catch {
            // localStorage unavailable (private mode etc) — treat as unverified
        }
        setStatus({ mounted: true, alreadyVerified })
    }, [])

    const open = status.mounted && !status.alreadyVerified && !dismissed

    if (!open) return null

    const confirm = () => {
        try { localStorage.setItem(STORAGE_KEY, '1') } catch {}
        setClosing(true)
        window.setTimeout(() => {
            setDismissed(true)
            router.push('/')
        }, 400)
    }

    return (
        <div
            className={cn(
                'fixed inset-0 z-[200] flex items-center justify-center bg-hc-canopy-2 p-6 transition-opacity duration-500',
                closing ? 'opacity-0 pointer-events-none' : 'opacity-100',
            )}
            role="dialog"
            aria-modal="true"
            aria-label="Age verification"
        >
            <div
                className="pointer-events-none absolute inset-0"
                style={{
                    background: 'radial-gradient(60% 50% at 50% 38%, rgba(200,121,46,.28), transparent 70%)',
                }}
            />
            <div className="relative max-w-[420px] w-full text-center text-hc-paper">
                <div
                    className="mx-auto mb-6 h-11 w-11 rounded-full"
                    style={{
                        background: 'radial-gradient(circle at 32% 28%, var(--color-hc-amber-light), var(--color-hc-amber) 60%, var(--color-hc-amber-dim))',
                        boxShadow: '0 0 40px rgba(200,121,46,.45)',
                    }}
                />
                <h1 className="font-hc-display text-3xl sm:text-4xl font-medium leading-tight mb-3">
                    Welcome to HappyCana
                </h1>
                <p className="text-hc-sage text-[15px] leading-relaxed mb-8">
                    Please confirm your age before entering. This site is intended for adults 21 and older, in states where cannabis is legal.
                </p>

                {!blocked ? (
                    <div className="flex gap-3 justify-center flex-wrap">
                        <button
                            onClick={confirm}
                            className="inline-flex items-center justify-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-transform hover:-translate-y-0.5"
                            style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }}
                        >
                            I&rsquo;m 21 or older
                        </button>
                        <button
                            onClick={() => setBlocked(true)}
                            className="inline-flex items-center justify-center gap-2 rounded-full border border-hc-paper/35 bg-hc-paper/[0.04] px-6 py-3 text-sm font-semibold text-hc-paper transition-colors hover:bg-hc-paper/10"
                        >
                            I&rsquo;m under 21
                        </button>
                    </div>
                ) : (
                    <div className="rounded-xl border border-hc-paper/15 bg-black/25 px-4 py-3.5 text-sm leading-relaxed text-hc-paper">
                        You must be 21 or older to enter this site. If you&rsquo;re looking for information on substance use,
                        the SAMHSA National Helpline (1-800-662-4357) is free, confidential, and available 24/7.
                    </div>
                )}

                <p className="mt-6 font-hc-mono text-[11px] tracking-wide text-hc-sage-dim">
                    LICENSED CANNABIS RETAILER · STATE LICENSE #AD-2291-HC
                </p>
            </div>
        </div>
    )
}