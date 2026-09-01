'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'

import { ChevronLeft, ShoppingBag, X } from 'lucide-react'
import { useOrder, useCancelOrder } from '@/hooks/useApi'
import { useOrderStatusWS } from '@/hooks/useWebSocket'
import { formatPrice, formatDate, ORDER_STATUS_LABEL, ORDER_STATUS_COLOR, getVariantLabel, cn, mediaUrl } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

const STEPS = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']

export default function OrderDetailPage() {
    const { id }                     = useParams<{ id: string }>()
    const { data: order, isLoading } = useOrder(id)
    const cancelOrder                = useCancelOrder()
    useOrderStatusWS(id)

    if (isLoading) return (
        <div className="space-y-6">
            <Skeleton className="h-8 w-1/3" />
            <Skeleton className="h-40 w-full rounded-xl" />
            <Skeleton className="h-60 w-full rounded-xl" />
        </div>
    )

    if (!order) return (
        <div className="text-center py-20">
            <p className="text-muted-foreground">Order not found.</p>
            <Button asChild size="sm" className="mt-4"><Link href="/account/orders">Back to orders</Link></Button>
        </div>
    )

    const currentStep = STEPS.indexOf(order.status)

    return (
        <div className="space-y-6">
            <Button asChild variant="ghost" size="sm" className="-ml-2">
                <Link href="/account/orders"><ChevronLeft className="h-4 w-4 mr-1" />All Orders</Link>
            </Button>

            {/* Header */}
            <div className="flex items-start justify-between gap-4 flex-wrap">
                <div>
                    <h1 className="font-display text-2xl font-semibold">Order #{order.id.slice(0, 8).toUpperCase()}</h1>
                    <p className="text-muted-foreground text-sm mt-1">Placed on {formatDate(order.created_at)}</p>
                </div>
                <div className="flex items-center gap-3">
                    <Badge className={cn('text-sm px-3 py-1', ORDER_STATUS_COLOR[order.status])}>
                        {ORDER_STATUS_LABEL[order.status]}
                    </Badge>
                    {['pending', 'confirmed'].includes(order.status) && (
                        <Button variant="destructive" size="sm"
                                onClick={() => cancelOrder.mutate(order.id)} disabled={cancelOrder.isPending}>
                            <X className="h-3.5 w-3.5 mr-1" /> Cancel
                        </Button>
                    )}
                </div>
            </div>

            {/* Progress tracker */}
            {!['cancelled', 'refunded'].includes(order.status) && (
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center">
                            {STEPS.map((step, i) => (
                                <div key={step} className="flex-1 flex items-center">
                                    <div className="flex flex-col items-center">
                                        <div className={cn(
                                            'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors',
                                            i <= currentStep ? 'bg-brand-600 border-brand-600 text-white' : 'bg-background border-border text-muted-foreground'
                                        )}>
                                            {i < currentStep ? '✓' : i + 1}
                                        </div>
                                        <p className={cn('mt-2 text-[10px] font-medium capitalize hidden sm:block',
                                            i <= currentStep ? 'text-brand-700' : 'text-muted-foreground')}>
                                            {step}
                                        </p>
                                    </div>
                                    {i < STEPS.length - 1 && (
                                        <div className={cn('flex-1 h-0.5 mx-1 transition-colors',
                                            i < currentStep ? 'bg-brand-500' : 'bg-border')} />
                                    )}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Items */}
            <Card>
                <CardHeader><CardTitle>Items</CardTitle></CardHeader>
                <CardContent className="pt-0">
                    <div className="divide-y">
                        {order.items?.map(item => (
                            <div key={item.id} className="flex items-center gap-4 py-4 first:pt-0 last:pb-0">
                                <div className="h-16 w-16 rounded-xl overflow-hidden bg-muted shrink-0">
                                    {item.variant.primary_image?.image_url ? (
                                        <Image src={mediaUrl(item.variant.primary_image.image_url)!} alt={item.variant.product?.name ?? ''} width={64} height={64} quality={50} className="h-full w-full object-cover" />
                                    ) : (
                                        <div className="h-full w-full flex items-center justify-center">
                                            <ShoppingBag className="h-6 w-6 text-muted-foreground/40" />
                                        </div>
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-sm">{item.variant.product?.name}</p>
                                    <p className="text-xs text-muted-foreground mt-0.5">{getVariantLabel(item.variant)}</p>
                                    <p className="text-xs text-muted-foreground mt-0.5">
                                        {formatPrice(item.unit_price)} × {item.quantity}
                                    </p>
                                </div>
                                <p className="font-semibold">{formatPrice(item.total_price)}</p>
                            </div>
                        ))}
                    </div>

                    <Separator className="my-4" />

                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Subtotal</span>
                            <span>{formatPrice(order.subtotal)}</span>
                        </div>
                        {parseFloat(order.discount_amount) > 0 && (
                            <div className="flex justify-between text-brand-700">
                                <span>Discount</span>
                                <span>−{formatPrice(order.discount_amount)}</span>
                            </div>
                        )}
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Shipping</span>
                            <span>{formatPrice(order.shipping_cost)}</span>
                        </div>
                        <Separator />
                        <div className="flex justify-between font-semibold text-base">
                            <span>Total</span>
                            <span>{formatPrice(order.total)}</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Address */}
            {order.address && (
                <Card>
                    <CardHeader><CardTitle>Delivery Address</CardTitle></CardHeader>
                    <CardContent className="pt-0">
                        <address className="not-italic text-sm text-muted-foreground space-y-1">
                            <p>{order.address.line1}</p>
                            {order.address.line2 && <p>{order.address.line2}</p>}
                            <p>{order.address.city}, {order.address.state} {order.address.postal_code}</p>
                            <p>{order.address.country}</p>
                        </address>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}