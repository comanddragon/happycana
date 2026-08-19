'use client'

import Link from 'next/link'
import { Package, ChevronRight } from 'lucide-react'
import { useOrders } from '@/hooks/useApi'
import { formatPrice, formatDate, ORDER_STATUS_LABEL, ORDER_STATUS_COLOR, cn } from '@/lib/utils'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

export default function OrdersPage() {
    const { data, isLoading } = useOrders()

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-display font-semibold">Your Orders</h1>

            {isLoading && (
                <div className="space-y-4">
                    {[1, 2, 3].map(i => (
                        <Card key={i}><CardContent className="p-6 space-y-3">
                            <Skeleton className="h-4 w-1/4" />
                            <Skeleton className="h-4 w-1/2" />
                            <Skeleton className="h-4 w-1/3" />
                        </CardContent></Card>
                    ))}
                </div>
            )}

            {!isLoading && data?.results.length === 0 && (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                        <Package className="h-12 w-12 text-muted-foreground/40 mb-4" />
                        <h3 className="font-display text-xl font-medium">No orders yet</h3>
                        <p className="text-muted-foreground mt-1 text-sm">When you place orders, they&apos;ll appear here.</p>
                        <Button asChild size="sm" className="mt-6"><Link href="/shop/products">Start Shopping</Link></Button>
                    </CardContent>
                </Card>
            )}

            <div className="space-y-3">
                {data?.results.map(order => (
                    <Link key={order.id} href={`/account/orders/${order.id}`}>
                        <Card className="hover:shadow-md transition-shadow cursor-pointer group">
                            <CardContent className="p-6">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="space-y-1.5 flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs text-muted-foreground">
                        #{order.id.slice(0, 8).toUpperCase()}
                      </span>
                                            <Badge className={cn(ORDER_STATUS_COLOR[order.status])}>
                                                {ORDER_STATUS_LABEL[order.status] ?? order.status}
                                            </Badge>
                                        </div>
                                        <p className="font-semibold">
                                            {order.items?.length} item{order.items?.length !== 1 ? 's' : ''} · {formatPrice(order.total)}
                                        </p>
                                        <p className="text-sm text-muted-foreground">{formatDate(order.created_at)}</p>
                                    </div>
                                    <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-brand-600 transition-colors shrink-0 mt-1" />
                                </div>
                            </CardContent>
                        </Card>
                    </Link>
                ))}
            </div>
        </div>
    )
}