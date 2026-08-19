'use client'
// hooks/useWebSocket.ts
// Exactly matches realtime/routing.py and each consumer's send_json calls.
//
// Backend WS URLs (from realtime/routing.py):
//   ws/orders/<order_id>/     → OrderStatusConsumer
//   ws/inventory/             → InventoryConsumer  (admin only)
//   ws/notifications/         → NotificationConsumer
//   ws/chat/<room_id>/        → ChatConsumer
//
// Auth: JWT token passed as ?token=<access_token> query param
//   handled by JWTAuthMiddleware — connections without a valid token
//   are rejected with close code 4001.

import { useEffect, useRef, useCallback, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import Cookies from 'js-cookie'
import { toast } from 'sonner'
import { qk } from './useApi'

// ─── Types matching backend send_json payloads ────────────────────────────────

type WSMessage = {
    type: string
    payload: Record<string, unknown>
}

// ─── Shared helpers ───────────────────────────────────────────────────────────

const WS_BASE = (process.env.NEXT_PUBLIC_WS_URL)

function getToken() {
    return Cookies.get('access_token') ?? null
}

/**
 * Generic reconnecting WebSocket factory.
 * Returns a cleanup function.
 */
function createReconnectingWS(
    url: string,
    onMessage: (msg: WSMessage) => void,
    wsRef: React.MutableRefObject<WebSocket | null>,
    maxRetries = 5,
): () => void {
    let retries = 0
    let closed  = false
    let timer: ReturnType<typeof setTimeout> | null = null

    function connect() {
        if (closed) return
        const ws = new WebSocket(url)
        wsRef.current = ws

        ws.onopen = () => { retries = 0 }

        ws.onmessage = (e) => {
            try { onMessage(JSON.parse(e.data)) } catch {}
        }

        ws.onclose = (e) => {
            if (closed || e.code === 4001 || e.code === 4003) return
            if (retries < maxRetries) {
                retries++
                timer = setTimeout(connect, Math.min(1_000 * 2 ** retries, 30_000))
            }
        }

        ws.onerror = () => ws.close()
    }

    // Small delay so React Strict Mode's fake unmount fires before we connect.
    // In production this is negligible; in dev it prevents the "closed before
    // connection established" noise.
    timer = setTimeout(connect, 100)

    return () => {
        closed = true
        if (timer) clearTimeout(timer)
        wsRef.current?.close()
        wsRef.current = null
    }
}

// =============================================================================
// useOrderStatusWS
// Backend: ws/orders/<order_id>/
// Sends:   { type: "order.status_changed", payload: { order_id, status } }
//          { type: "connection.established", payload: { order_id } }
// =============================================================================

export function useOrderStatusWS(orderId: string | null) {
    const qc    = useQueryClient()
    const wsRef = useRef<WebSocket | null>(null)

    const handleMessage = useCallback((msg: WSMessage) => {
        if (msg.type === 'order.status_changed') {
            const status = msg.payload.status as string
            qc.invalidateQueries({ queryKey: qk.order(orderId!) })
            qc.invalidateQueries({ queryKey: qk.orders() })
            toast.success(`Order status: ${status.charAt(0).toUpperCase() + status.slice(1)}`)
        }
    }, [orderId, qc])

    useEffect(() => {
        if (!orderId) return
        const token = getToken()
        if (!token) return

        const url = `${WS_BASE}/orders/${orderId}/?token=${token}`
        return createReconnectingWS(url, handleMessage, wsRef)
    }, [orderId, handleMessage])
}

// =============================================================================
// useNotificationsWS
// Backend: ws/notifications/
// Sends:   { type: "notification_new",   payload: { id, type, title, body, created_at } }
//          { type: "notification_count", payload: { unread_count } }
//          { type: "connection.established", payload: { unread_count } }
// =============================================================================

export function useNotificationsWS() {
    const qc    = useQueryClient()
    const wsRef = useRef<WebSocket | null>(null)

    const handleMessage = useCallback((msg: WSMessage) => {
        if (msg.type === 'notification_new') {
            qc.invalidateQueries({ queryKey: qk.notifications() })
            const title = msg.payload.title as string | undefined
            if (title) toast(title, { icon: '🔔', description: msg.payload.body as string | undefined })
        }
        if (msg.type === 'notification_count') {
            qc.invalidateQueries({ queryKey: qk.notifications() })
        }
    }, [qc])

    useEffect(() => {
        const token = getToken()
        if (!token) return

        const url = `${WS_BASE}/notifications/?token=${token}`
        return createReconnectingWS(url, handleMessage, wsRef)
    }, [handleMessage])
}

// =============================================================================
// useInventoryWS  (admin only)
// Backend: ws/inventory/
// Sends:   { type: "inventory_stock_updated", payload: { sku, quantity, reserved, available, warehouse } }
//          { type: "inventory_low_stock",     payload: { sku, available, threshold, warehouse } }
// Rejects non-staff users with close code 4003.
// =============================================================================

export function useInventoryWS() {
    const qc    = useQueryClient()
    const wsRef = useRef<WebSocket | null>(null)

    const handleMessage = useCallback((msg: WSMessage) => {
        if (msg.type === 'inventory_stock_updated') {
            qc.invalidateQueries({ queryKey: ['products'] })
            qc.invalidateQueries({ queryKey: ['product'] })
        }
        if (msg.type === 'inventory_low_stock') {
            const { sku, available, threshold } = msg.payload
            toast.error(
                `Low stock: ${sku} — only ${available} left (threshold: ${threshold})`,
                { duration: 6000 }
            )
        }
    }, [qc])

    useEffect(() => {
        const token = getToken()
        if (!token) return

        const url = `${WS_BASE}/inventory/?token=${token}`
        return createReconnectingWS(url, handleMessage, wsRef)
    }, [handleMessage])
}

// =============================================================================
// useChatWS
// Backend: ws/chat/<room_id>/
// Client sends:    { action: "send_message", message: "..." }
//                  { action: "typing", is_typing: true }
// Client receives: { type: "chat.message", payload: { sender, message, timestamp } }
//                  { type: "chat.typing",  payload: { sender, is_typing } }
//                  { type: "chat.join",    payload: { sender } }
//                  { type: "chat.leave",   payload: { sender } }
// =============================================================================

export type ChatMessage = {
    sender: string
    message: string
    timestamp: string
}

export type TypingState = {
    sender: string
    is_typing: boolean
}

export function useChatWS(roomId: string | null) {
    const wsRef      = useRef<WebSocket | null>(null)
    const mountedRef = useRef(true)
    const [messages,  setMessages]  = useState<ChatMessage[]>([])
    const [typing,    setTyping]    = useState<TypingState | null>(null)
    const [connected, setConnected] = useState(false)

    // Track mounted state to guard all setState calls
    useEffect(() => {
        mountedRef.current = true
        return () => { mountedRef.current = false }
    }, [])

    const handleMessage = useCallback((msg: WSMessage) => {
        if (!mountedRef.current) return
        switch (msg.type) {
            case 'connection.established':
                setConnected(true)
                break
            case 'chat.message':
                setMessages(prev => [...prev, msg.payload as unknown as ChatMessage])
                break
            case 'chat.typing':
                setTyping(msg.payload as unknown as TypingState)
                setTimeout(() => { if (mountedRef.current) setTyping(null) }, 3000)
                break
        }
    }, [])

    useEffect(() => {
        if (!roomId) return
        const token = getToken()
        if (!token) return

        const url = `${WS_BASE}/chat/${roomId}/?token=${token}`
        const cleanup = createReconnectingWS(url, handleMessage, wsRef)
        return cleanup
    }, [roomId, handleMessage])

    const sendMessage = useCallback((message: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'send_message', message }))
        }
    }, [])

    const sendTyping = useCallback((is_typing: boolean) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'typing', is_typing }))
        }
    }, [])

    return { messages, typing, connected, sendMessage, sendTyping }
}