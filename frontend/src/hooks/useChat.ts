// hooks/useChat.ts
// Follows the same React Query + toast pattern as useApi.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useCallback, useState } from 'react'
import { toast } from 'sonner'
import Cookies from 'js-cookie'
import { extractErrorMessage } from '@/lib/api'
import { chatService } from '@/lib/services'
import { getWsBase } from '@/hooks/useWebSocket'
import type { WSChatMessage } from '@/types'

// ─── Query keys ───────────────────────────────────────────────────────────────

export const chatQk = {
    rooms:    (params?: object) => ['chat-rooms', params],
    room:     (id: string)      => ['chat-room', id],
    messages: (roomId: string)  => ['chat-messages', roomId],
} as const

// ─── REST hooks ───────────────────────────────────────────────────────────────

export function useChatRooms(params?: { status?: string }, enabled = true) {
    return useQuery({
        queryKey: chatQk.rooms(params),
        queryFn:  () => chatService.listRooms(params),
        enabled,
        staleTime: 15_000,
        refetchInterval: 30_000,
    })
}

export function useChatRoom(id: string | null) {
    return useQuery({
        queryKey: chatQk.room(id!),
        queryFn:  () => chatService.getRoom(id!),
        enabled:  !!id,
        staleTime: 10_000,
    })
}

export function useCreateChatRoom() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (payload: { subject: string; order?: string }) =>
            chatService.createRoom(payload),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: chatQk.rooms() })
            toast.success('chat room opened')
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

export function useResolveRoom() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (id: string) => chatService.resolveRoom(id),
        onSuccess: (room) => {
            qc.invalidateQueries({ queryKey: chatQk.rooms() })
            qc.invalidateQueries({ queryKey: chatQk.room(room.id) })
            toast.success('Conversation resolved')
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

// ─── WebSocket hook ───────────────────────────────────────────────────────────

const WS_BASE = getWsBase()

function getToken() {
    return Cookies.get('access_token') ?? null
}

export type ChatWsState = {
    messages: WSChatMessage[]
    typers: string[]
    connected: boolean
    /** True when the socket was rejected (4001 no/invalid token, 4003 not a
     *  participant) rather than just dropped by the network. Reconnecting
     *  with the same token/room won't help — the caller should prompt a
     *  refresh or bail out of the room instead of showing "Connecting...". */
    authError: boolean
    sendMessage: (body: string, messageType?: string) => void
    sendTyping: (isTyping: boolean) => void
    markRead: () => void
}

export function useChatRoomWS(roomId: string | null): ChatWsState {
    const wsRef      = useRef<WebSocket | null>(null)
    const mountedRef = useRef(true)
    const retriesRef = useRef(0)
    const timerRef   = useRef<ReturnType<typeof setTimeout> | null>(null)
    const closedRef  = useRef(false)

    const [messages,  setMessages]  = useState<WSChatMessage[]>([])
    const [typers,    setTypers]    = useState<string[]>([])
    const [connected, setConnected] = useState(false)
    const [authError, setAuthError] = useState(false)

    useEffect(() => {
        mountedRef.current = true
        return () => { mountedRef.current = false }
    }, [])

    const handleMessage = useCallback((raw: string) => {
        if (!mountedRef.current) return
        try {
            const msg = JSON.parse(raw)
            switch (msg.type) {
                case 'chat.history':
                    setMessages(msg.payload.messages ?? [])
                    setConnected(true)
                    break
                case 'chat.message': {
                    const incoming = msg.payload as WSChatMessage
                    setMessages(prev => {
                        // Deduplicate by id in case REST fallback already added it
                        if (prev.some(m => m.id === incoming.id)) return prev
                        return [...prev, incoming]
                    })
                    break
                }
                case 'chat.typing': {
                    const { sender, is_typing } = msg.payload as { sender: string; is_typing: boolean }
                    setTypers(prev =>
                        is_typing
                            ? prev.includes(sender) ? prev : [...prev, sender]
                            : prev.filter(s => s !== sender)
                    )
                    // Auto-clear typing after 4s in case leave event is missed
                    setTimeout(() => {
                        if (mountedRef.current)
                            setTypers(prev => prev.filter(s => s !== sender))
                    }, 4000)
                    break
                }
                case 'chat.join':
                case 'chat.leave':
                case 'chat.read':
                    // could invalidate query or show toast — kept silent for now
                    break
                case 'connection.established':
                    setConnected(true)
                    break
            }
        } catch {}
    }, [])

    // Connect / reconnect
    useEffect(() => {
        if (!roomId) return
        const token = getToken()
        if (!token) return

        closedRef.current = false
        retriesRef.current = 0
        setAuthError(false)

        function connect() {
            if (closedRef.current) return
            const url = `${WS_BASE}/chat/${roomId}/?token=${token}`
            const ws  = new WebSocket(url)
            wsRef.current = ws

            ws.onopen  = () => { retriesRef.current = 0; setConnected(true) }
            ws.onmessage = (e) => handleMessage(e.data)
            ws.onclose = (e) => {
                setConnected(false)
                if (closedRef.current) return
                // 4001 = no/invalid token, 4003 = authenticated but not a participant
                // in this room. Both are terminal — retrying with the same token
                // and room id will never succeed, so stop and surface it instead
                // of leaving the UI stuck on "Connecting..." forever.
                if (e.code === 4001 || e.code === 4003) {
                    setAuthError(true)
                    toast.error(
                        e.code === 4001
                            ? 'Chat session expired — refresh the page to reconnect.'
                            : "You don't have access to this conversation."
                    )
                    return
                }
                if (retriesRef.current < 5) {
                    retriesRef.current++
                    timerRef.current = setTimeout(connect, Math.min(1000 * 2 ** retriesRef.current, 30_000))
                }
            }
            ws.onerror = () => ws.close()
        }

        timerRef.current = setTimeout(connect, 100)

        return () => {
            closedRef.current = true
            if (timerRef.current) clearTimeout(timerRef.current)
            wsRef.current?.close()
            wsRef.current = null
            setConnected(false)
            setMessages([])
            setTypers([])
            setAuthError(false)
        }
    }, [roomId, handleMessage])

    const sendMessage = useCallback((body: string, messageType = 'text') => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'send_message', body, message_type: messageType }))
        }
    }, [])

    const sendTyping = useCallback((isTyping: boolean) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'typing', is_typing: isTyping }))
        }
    }, [])

    const markRead = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'read_messages' }))
        }
    }, [])

    return { messages, typers, connected, authError, sendMessage, sendTyping, markRead }
}