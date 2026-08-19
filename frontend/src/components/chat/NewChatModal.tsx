'use client'

import { useState } from 'react'
import { Loader2,} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Dialog, DialogContent, DialogHeader,
    DialogTitle, DialogDescription,
} from '@/components/ui/dialog'
import { useOrders } from '@/hooks/useApi'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface NewChatModalProps {
    onClose: () => void
    onSubmit: (subject: string, orderId?: string) => Promise<void>
    isLoading?: boolean
}

export function NewChatModal({ onClose, onSubmit, isLoading }: NewChatModalProps) {
    const [subject,  setSubject]  = useState('')
    const [orderId,  setOrderId]  = useState<string | undefined>(undefined)
    const NONE = '__none__'

    const { data: ordersData } = useOrders()

    const handleSubmit = async () => {
        if (!subject.trim()) return
        await onSubmit(subject.trim(), orderId)
    }

    return (
        <Dialog open onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="font-display">Start a conversation</DialogTitle>
                    <DialogDescription>
                        Describe your issue briefly. Our support team will respond shortly.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-2">
                    {/* Subject */}
                    <div className="space-y-1.5">
                        <Label htmlFor="subject">Subject <span className="text-destructive">*</span></Label>
                        <Input
                            id="subject"
                            placeholder="e.g. My order hasn't shipped yet"
                            value={subject}
                            onChange={e => setSubject(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                            autoFocus
                        />
                    </div>

                    {/* Optional order link */}
                    {ordersData && ordersData.results.length > 0 && (
                        <div className="space-y-1.5">
                            <Label htmlFor="order">Related order <span className="text-surface-400 font-normal">(optional)</span></Label>
                            <Select value={orderId ?? NONE} onValueChange={val => setOrderId(val === NONE ? undefined : val)}>
                                <SelectTrigger id="order">
                                    <SelectValue placeholder="Select an order…" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value={NONE}>None</SelectItem>
                                    {ordersData.results.map(order => (
                                        <SelectItem key={order.id} value={order.id}>
                                            #{order.id.slice(0, 8).toUpperCase()} — {order.status} — ${order.total}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    )}
                </div>

                <div className="flex justify-end gap-2 pt-2">
                    <Button variant="outline" onClick={onClose} disabled={isLoading}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={!subject.trim() || isLoading}
                        className="gap-2"
                    >
                        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                        Open Chat
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    )
}