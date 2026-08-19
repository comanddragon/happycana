'use client'

import { memo, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'

import { ShoppingBag, Trash2, Plus, Minus, ArrowRight } from 'lucide-react'
import { useCartStore } from '@/store/cart'
import { useCart, useUpdateCartItem, useRemoveCartItem } from '@/hooks/useApi'
import { formatPrice, getVariantLabel, mediaUrl } from '@/lib/utils'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'

import type { CartItem } from '@/types'

function getCartItemImage(item: CartItem): string | null {
    return (
        item.variant.images?.find(img => img.is_primary)?.image_url ||
        item.variant.product?.primary_image?.image_url ||
        item.variant.product?.images?.[0]?.image_url ||
        null
    )
}

const CartLineItem = memo(function CartLineItem({
    item,
    onUpdateQuantity,
    onRemove,
}: {
    item: CartItem
    onUpdateQuantity: (id: string, quantity: number) => void
    onRemove: (id: string) => void
}) {
    const img = getCartItemImage(item)

    return (
        <div className="flex gap-3">
            <div className="h-20 w-20 shrink-0 rounded-xl overflow-hidden bg-hc-paper-2">
                {img ? (
                    <Image src={mediaUrl(img)!} alt={item.variant.product?.name ?? ''}
                           width={80} height={80} unoptimized className="h-full w-full object-cover" />
                ) : (
                    <div className="h-full w-full flex items-center justify-center">
                        <ShoppingBag className="h-6 w-6 text-hc-ink-soft" />
                    </div>
                )}
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.variant.product?.name}</p>
                {item.variant.attributes?.length > 0 ? (
                    <p className="text-xs text-muted-foreground mt-0.5">
                        {getVariantLabel(item.variant)}
                    </p>
                ) : null}
                <p className="text-sm font-semibold text-hc-amber-dim mt-1">{formatPrice(item.subtotal)}</p>
                <div className="flex items-center gap-2 mt-2">
                    <div className="flex items-center rounded-md border overflow-hidden">
                        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-none"
                                onClick={() => item.quantity <= 1 ? onRemove(item.id) : onUpdateQuantity(item.id, item.quantity - 1)}
                                aria-label="Decrease quantity">
                            <Minus className="h-3 w-3" />
                        </Button>
                        <span className="px-2 text-xs font-medium min-w-[24px] text-center tabular-nums">{item.quantity}</span>
                        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-none"
                                onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                                aria-label="Increase quantity">
                            <Plus className="h-3 w-3" />
                        </Button>
                    </div>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive"
                            onClick={() => onRemove(item.id)}
                            aria-label="Remove item">
                        <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                </div>
            </div>
        </div>
    )
})

export function CartDrawer() {
    const { isOpen, closeCart } = useCartStore()
    const { data: cart, isLoading } = useCart()
    const updateItem = useUpdateCartItem()
    const removeItem = useRemoveCartItem()

    const handleUpdateQuantity = useCallback((id: string, quantity: number) => {
        updateItem.mutate({ id, quantity })
    }, [updateItem])

    const handleRemove = useCallback((id: string) => {
        removeItem.mutate(id)
    }, [removeItem])

    return (
        <Sheet open={isOpen} onOpenChange={open => !open && closeCart()}>
            <SheetContent side="right" className="w-full max-w-sm flex flex-col p-0 bg-hc-paper text-hc-ink border-l border-hc-ink/10">
                <SheetHeader className="px-5 py-4 border-b border-hc-ink/10">
                    <SheetTitle className="flex items-center gap-2 font-hc-display text-lg font-medium">
                        <ShoppingBag className="h-5 w-5 text-hc-amber-dim" />
                        Your Cart
                        {cart && cart.item_count > 0 && (
                            <Badge className="bg-hc-amber-light/20 text-hc-amber-dim border-0">{cart.item_count}</Badge>
                        )}
                    </SheetTitle>
                    <SheetDescription className="sr-only">
                        Review and manage items in your shopping cart
                    </SheetDescription>
                </SheetHeader>

                {/* Items */}
                <ScrollArea className="flex-1 px-5 py-4">
                    {isLoading && (
                        <div className="space-y-4">
                            {[1, 2].map(i => (
                                <div key={i} className="flex gap-3">
                                    <Skeleton className="h-20 w-20 rounded-xl" />
                                    <div className="flex-1 space-y-2 pt-1">
                                        <Skeleton className="h-4 w-3/4" />
                                        <Skeleton className="h-3 w-1/2" />
                                        <Skeleton className="h-4 w-1/3" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {!isLoading && (!cart || cart.items.length === 0) && (
                        <div className="flex flex-col items-center justify-center h-64 gap-4 text-center">
                            <div className="h-16 w-16 rounded-2xl bg-hc-paper-2 flex items-center justify-center">
                                <ShoppingBag className="h-8 w-8 text-hc-ink-soft" />
                            </div>
                            <div>
                                <p className="font-medium">Your cart is empty</p>
                                <p className="text-sm text-muted-foreground mt-1">Add some products to get started</p>
                            </div>
                            <Button asChild size="sm" className="rounded-full text-hc-canopy-2 font-semibold" style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }} onClick={closeCart}>
                                <Link href="/shop/products">Browse Products</Link>
                            </Button>
                        </div>
                    )}

                    <div className="space-y-4">
                        {cart?.items.map(item => (
                            <CartLineItem
                                key={item.id}
                                item={item}
                                onUpdateQuantity={handleUpdateQuantity}
                                onRemove={handleRemove}
                            />
                        ))}
                    </div>
                </ScrollArea>

                {/* Footer */}
                {cart && cart.items.length > 0 && (
                    <div className="border-t border-hc-ink/10 px-5 py-4 space-y-3 bg-hc-paper-2/60">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Subtotal</span>
                            <span className="font-semibold">{formatPrice(cart.total_price)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Shipping and taxes calculated at checkout</p>
                        <Separator />
                        <Button asChild className="w-full rounded-full text-hc-canopy-2 font-semibold" style={{ background: 'linear-gradient(180deg, var(--color-hc-amber-light), var(--color-hc-amber))' }} onClick={closeCart}>
                            <Link href="/shop/checkout" className="flex items-center justify-between">
                                <span>Checkout</span>
                                <ArrowRight className="h-4 w-4" />
                            </Link>
                        </Button>
                    </div>
                )}
            </SheetContent>
        </Sheet>
    )
}