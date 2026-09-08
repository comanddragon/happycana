'use client'

import { useRef, useState } from 'react'
import { MessageCircle, X, Loader2 } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { useChatRooms, useCreateChatRoom } from '@/hooks/useChat'
import { useClickOutside } from '@/hooks/useClickOutside'
import { ensureGuestSession } from '@/lib/guestSession'
import { ChatRoomList } from './ChatRoomList'
import { ChatWindow } from './ChatWindow'
import { NewChatModal } from './NewChatModal'
import { Button } from '@/components/ui/button'
import type { ChatRoom } from '@/types'

export function FloatingChatButton() {
    const containerRef = useRef<HTMLDivElement>(null)
    const [isOpen, setIsOpen] = useState(false)
    const [activeRoomId, setActiveRoomId] = useState<string | null>(null)
    const [showNewModal, setShowNewModal] = useState(false)
    const [isBootstrapping, setIsBootstrapping] = useState(false)

    const isAuthenticated = useAuthStore(s => s.isAuthenticated)
    // Anonymous visitors have no session yet — don't fire an auth-required
    // request (and risk the 401 interceptor bouncing them to /login) until
    // handleToggle has actually bootstrapped one.
    const { data, isLoading } = useChatRooms(undefined, isAuthenticated)
    const createRoom = useCreateChatRoom()

    useClickOutside(containerRef, () => setIsOpen(false))

    const rooms = data?.results ?? []
    const activeRoom: ChatRoom | null = rooms.find(r => r.id === activeRoomId) ?? null
    const unreadCount = rooms.reduce((sum, r) => sum + r.unread_count, 0)

    const handleSelectRoom = (room: ChatRoom) => setActiveRoomId(room.id)

    const handleCreateRoom = async (subject: string, orderId?: string) => {
        const room = await createRoom.mutateAsync({ subject, order: orderId })
        setActiveRoomId(room.id)
        setShowNewModal(false)
    }

    /** Opens the widget and jumps straight into a conversation — no room
     *  list, no "start a chat" modal in the way. First-time guests get a
     *  session bootstrapped and a fresh room. Everyone else lands in their
     *  most recent room (rooms are ordered -updated_at server-side), or a
     *  fresh one if they've never chatted before. */
    const handleToggle = async () => {
        if (isOpen) {
            setIsOpen(false)
            return
        }
        if (!isAuthenticated) {
            setIsBootstrapping(true)
            try {
                await ensureGuestSession()
                const room = await createRoom.mutateAsync({ subject: 'Support chat' })
                setActiveRoomId(room.id)
                setIsOpen(true)
            } finally {
                setIsBootstrapping(false)
            }
            return
        }
        setIsBootstrapping(true)
        try {
            const existing = rooms[0]
            if (existing) {
                setActiveRoomId(existing.id)
            } else {
                const room = await createRoom.mutateAsync({ subject: 'Support chat' })
                setActiveRoomId(room.id)
            }
            setIsOpen(true)
        } finally {
            setIsBootstrapping(false)
        }
    }

    return (
        <div ref={containerRef}>
            <Button
                onClick={handleToggle}
                disabled={isBootstrapping}
                size="icon"
                className="fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-shadow"
                aria-label={isOpen ? 'Close chat' : 'Open chat'}
            >
                {isBootstrapping ? (
                    <Loader2 className="h-6 w-6 animate-spin" />
                ) : isOpen ? (
                    <X className="h-6 w-6" />
                ) : (
                    <MessageCircle className="h-6 w-6" />
                )}
                {!isOpen && !isBootstrapping && unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 h-5 min-w-5 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center tabular-nums">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </Button>

            {isOpen && (
                <div className="fixed bottom-24 right-6 z-50 w-[calc(100vw-3rem)] sm:w-96 h-[32rem] max-h-[calc(100vh-8rem)] rounded-2xl border border-border bg-white shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-200">
                    {activeRoom ? (
                        <ChatWindow
                            room={activeRoom}
                            onBack={() => setActiveRoomId(null)}
                            onRoomUpdate={(updated) => setActiveRoomId(updated.id)}
                        />
                    ) : (
                        <ChatRoomList
                            rooms={rooms}
                            isLoading={isLoading}
                            activeRoomId={null}
                            onSelect={handleSelectRoom}
                            onNew={() => setShowNewModal(true)}
                        />
                    )}
                </div>
            )}

            {showNewModal && (
                <NewChatModal
                    onClose={() => setShowNewModal(false)}
                    onSubmit={handleCreateRoom}
                    isLoading={createRoom.isPending}
                />
            )}
        </div>
    )
}
