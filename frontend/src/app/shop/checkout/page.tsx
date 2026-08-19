'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'
import {
    useCart, useAddresses, useShippingMethods,
    useValidateCoupon, useCheckout, useCreateAddress,
} from '@/hooks/useApi'
import { Reveal } from '@/components/home/Reveal'
import type { CheckoutPayload } from '@/types'
import { StepRail } from '@/components/checkout/StepRail'
import { AddressStep } from '@/components/checkout/AddressStep'
import { ShippingStep } from '@/components/checkout/ShippingStep'
import { PaymentStep } from '@/components/checkout/PaymentStep'
import { OrderSummary } from '@/components/checkout/OrderSummary'
import { EmptyCartState } from '@/components/checkout/EmptyCartState'
import type { PaymentGateway, CouponResult } from '@/components/checkout/types'
import type { AddressForm } from '@/lib/checkout/schema'

export default function CheckoutPage() {
    const router = useRouter()
    const { data: cart }       = useCart()
    const { data: addresses }  = useAddresses()
    const { data: methods }    = useShippingMethods()
    const validateCoupon       = useValidateCoupon()
    const checkout             = useCheckout()
    const createAddress        = useCreateAddress()

    const [selectedAddress,  setSelectedAddress]  = useState<string>('')
    const [selectedShipping, setSelectedShipping] = useState<string>('')
    const [couponCode,       setCouponCode]        = useState('')
    const [couponResult,     setCouponResult]      = useState<CouponResult | null>(null)
    const [gateway,          setGateway]           = useState<PaymentGateway>('stripe')
    const [newAddrOpen,      setNewAddrOpen]       = useState(false)

    const selectedMethod = methods?.find(m => m.id === selectedShipping)
    const subtotal       = parseFloat(cart?.total_price ?? '0')
    const discount       = parseFloat(couponResult?.discount_amount ?? '0')
    const shipping       = parseFloat(selectedMethod?.price ?? '0')
    const total          = Math.max(0, subtotal - discount + shipping)

    // Step completion — purely derived, no new state.
    const addressDone  = !!selectedAddress
    const shippingDone = addressDone && !!selectedShipping
    const paymentDone  = shippingDone && !!gateway

    const handleApplyCoupon = async () => {
        if (!couponCode.trim()) return
        try {
            const result = await validateCoupon.mutateAsync({
                code: couponCode.toUpperCase(),
                subtotal: cart?.total_price ?? '0',
            })
            setCouponResult(result)
            toast.success(result.summary)
        } catch {
            setCouponResult(null)
        }
    }

    const handleSaveAddress = async (data: AddressForm) => {
        const addr = await createAddress.mutateAsync({ ...data, is_default: false })
        setSelectedAddress(addr.id)
        setNewAddrOpen(false)
    }

    const handleCheckout = async () => {
        if (!selectedAddress) return toast.error('Please select a delivery address')
        if (!selectedShipping) return toast.error('Please select a shipping method')
        if (!cart?.items.length) return toast.error('Your cart is empty')

        const payload: CheckoutPayload = {
            address_id:        selectedAddress,
            // shipping_method_id: selectedShipping,
            coupon_code:       couponResult ? couponCode : undefined,
            gateway,
            cart_items: cart.items.map(i => ({ variant: i.variant.id, quantity: i.quantity })),
        }

        const result = await checkout.mutateAsync(payload)

        if (result.payment_url) {
            // PayPal — redirect to approval URL
            window.location.href = result.payment_url
        } else {
            // Stripe — redirect to order success (would normally load Stripe Elements)
            toast.success('Order placed!')
            router.push(`/account/orders/${result.order.id}`)
        }
    }

    // Empty-cart guard — cart has loaded and there's genuinely nothing to check out.
    if (cart && cart.items.length === 0) {
        return <EmptyCartState />
    }

    return (
        <div className="bg-hc-paper">
            <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">

                {/* Back */}
                <button
                    onClick={() => router.back()}
                    className="mb-6 inline-flex items-center gap-1.5 font-hc-mono text-xs uppercase tracking-wide text-hc-ink-soft transition-colors hover:text-hc-amber-dim"
                >
                    <ArrowLeft className="h-3.5 w-3.5" /> Back
                </button>

                {/* Header + step rail */}
                <div className="mb-9 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                        <div className="mb-2 inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                            Almost there
                        </div>
                        <h1 className="font-hc-display text-3xl font-normal text-hc-ink sm:text-4xl">Checkout</h1>
                    </div>
                    <StepRail addressDone={addressDone} shippingDone={shippingDone} paymentDone={paymentDone} />
                </div>

                <div className="grid gap-6 lg:grid-cols-5 lg:gap-8">
                    {/* Left col — the flow */}
                    <div className="space-y-5 lg:col-span-3">
                        <Reveal delay={0}>
                            <AddressStep
                                addresses={addresses}
                                selectedAddress={selectedAddress}
                                onSelectAddress={setSelectedAddress}
                                newAddrOpen={newAddrOpen}
                                onToggleNewAddr={() => setNewAddrOpen(o => !o)}
                                onSaveAddress={handleSaveAddress}
                                isSavingAddress={createAddress.isPending}
                            />
                        </Reveal>

                        <Reveal delay={80}>
                            <ShippingStep
                                methods={methods}
                                selectedShipping={selectedShipping}
                                onSelect={setSelectedShipping}
                                locked={!addressDone}
                            />
                        </Reveal>

                        <Reveal delay={160}>
                            <PaymentStep
                                gateway={gateway}
                                onSelect={setGateway}
                                locked={!shippingDone}
                            />
                        </Reveal>
                    </div>

                    {/* Order summary */}
                    <div className="lg:col-span-2">
                        <Reveal delay={240}>
                            <OrderSummary
                                cart={cart}
                                subtotal={subtotal}
                                discount={discount}
                                shipping={shipping}
                                total={total}
                                couponCode={couponCode}
                                onCouponCodeChange={setCouponCode}
                                couponResult={couponResult}
                                onApplyCoupon={handleApplyCoupon}
                                isApplyingCoupon={validateCoupon.isPending}
                                onCheckout={handleCheckout}
                                isCheckingOut={checkout.isPending}
                            />
                        </Reveal>
                    </div>
                </div>
            </div>
        </div>
    )
}