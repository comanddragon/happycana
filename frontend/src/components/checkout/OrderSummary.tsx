'use client'

import { Tag, Check, Loader2, ShieldCheck } from 'lucide-react'
import { cn, formatPrice } from '@/lib/utils'
import { AMBER_GRADIENT } from '@/lib/checkout/constants'
import type { Cart, CouponResult } from './types'
import Image from "next/image";

interface OrderSummaryProps {
    cart: Cart | undefined
    subtotal: number
    discount: number
    shipping: number
    total: number
    couponCode: string
    onCouponCodeChange: (value: string) => void
    couponResult: CouponResult | null
    onApplyCoupon: () => void
    isApplyingCoupon: boolean
    onCheckout: () => void
    isCheckingOut: boolean
}

export function OrderSummary({
    cart,
    subtotal,
    discount,
    shipping,
    total,
    couponCode,
    onCouponCodeChange,
    couponResult,
    onApplyCoupon,
    isApplyingCoupon,
    onCheckout,
    isCheckingOut,
}: OrderSummaryProps) {
    return (
        <div className="sticky top-24 rounded-2xl border border-hc-ink/[0.08] bg-white p-6 shadow-[0_20px_40px_-24px_rgba(23,20,15,0.2)]">
            <div className="mb-4 flex items-center justify-between">
                <h2 className="font-hc-display text-lg font-medium text-hc-ink">Order Summary</h2>
                <span className="font-hc-mono text-[11px] uppercase tracking-wide text-hc-ink-soft/60">Step 4</span>
            </div>

            {/* Items */}
            <div className="mb-4 max-h-48 space-y-3 overflow-y-auto pr-1">
                {cart?.items.map(item => (
                    <div key={item.id} className="flex items-center gap-3">
                        <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-lg bg-hc-paper-2">
                            {item.variant.images?.[0]?.image_url && (
                                <Image src={item.variant.images?.[0]?.image_url} alt="" fill quality={50} sizes="40px" className="object-cover" />
                            )}
                        </div>
                        <div className="min-w-0 flex-1">
                            <p className="truncate text-xs font-medium text-hc-ink">
                                {item.variant.product?.name}
                            </p>
                            <p className="font-hc-mono text-[11px] text-hc-ink-soft">×{item.quantity}</p>
                        </div>
                        <p className="font-hc-mono text-xs font-semibold text-hc-ink">{formatPrice(item.subtotal)}</p>
                    </div>
                ))}
            </div>

            <div className="space-y-2 border-t border-dashed border-hc-ink/15 pt-4">
                <div className="flex justify-between text-sm">
                    <span className="text-hc-ink-soft">Subtotal</span>
                    <span className="font-hc-mono font-medium text-hc-ink">{formatPrice(subtotal)}</span>
                </div>
                {couponResult && discount > 0 && (
                    <div className="flex justify-between text-sm text-hc-amber-dim">
                        <span>Discount</span>
                        <span className="font-hc-mono">−{formatPrice(discount)}</span>
                    </div>
                )}
                <div className="flex justify-between text-sm">
                    <span className="text-hc-ink-soft">Shipping</span>
                    <span className="font-hc-mono font-medium text-hc-ink">{shipping > 0 ? formatPrice(shipping) : '—'}</span>
                </div>
                <div className="mt-2 flex justify-between border-t border-dashed border-hc-ink/15 pt-2.5 text-base font-semibold">
                    <span className="font-hc-display text-hc-ink">Total</span>
                    <span className="font-hc-mono text-hc-ink">{formatPrice(total)}</span>
                </div>
            </div>

            {/* Coupon */}
            <div className="mt-4 flex gap-2">
                <div className="relative flex-1">
                    <Tag className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-hc-ink-soft/50" />
                    <input
                        type="text"
                        placeholder="Coupon code"
                        value={couponCode}
                        onChange={e => onCouponCodeChange(e.target.value.toUpperCase())}
                        className="w-full rounded-lg border border-hc-ink/15 bg-hc-paper py-2.5 pl-8 pr-3 font-hc-mono text-sm text-hc-ink placeholder:font-hc-body placeholder:text-hc-ink-soft/60 outline-none transition-colors focus:border-hc-amber focus:ring-2 focus:ring-hc-amber/15"
                    />
                </div>
                <button
                    onClick={onApplyCoupon}
                    disabled={isApplyingCoupon}
                    className="shrink-0 rounded-lg border border-hc-ink/15 px-4 text-sm font-medium text-hc-ink transition-colors hover:border-hc-amber hover:text-hc-amber-dim disabled:opacity-60"
                >
                    {isApplyingCoupon ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : 'Apply'}
                </button>
            </div>
            {couponResult && (
                <p className="mt-2 flex items-center gap-1.5 text-xs text-hc-amber-dim">
                    <Check className="h-3.5 w-3.5" />
                    {couponResult.summary}
                </p>
            )}

            <button
                onClick={onCheckout}
                disabled={isCheckingOut || !cart?.items.length}
                className={cn(
                    'mt-5 flex w-full items-center justify-center gap-2 rounded-full py-3.5 text-sm font-semibold text-hc-canopy-2 shadow-[0_6px_18px_rgba(200,121,46,.35)] transition-all duration-200',
                    isCheckingOut || !cart?.items.length
                        ? 'opacity-60'
                        : 'hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(200,121,46,.45)]',
                )}
                style={AMBER_GRADIENT}
            >
                {isCheckingOut ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> Processing…</>
                ) : (
                    <>Place Order · {formatPrice(total)}</>
                )}
            </button>

            <p className="mt-3 flex items-center justify-center gap-1.5 font-hc-mono text-[10.5px] uppercase tracking-wide text-hc-ink-soft/60">
                <ShieldCheck className="h-3 w-3" /> Encrypted checkout · Age-verified delivery
            </p>
        </div>
    )
}
