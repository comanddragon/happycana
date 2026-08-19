'use client'

import {useState, useEffect} from 'react'
import { MessageSquarePlus, Inbox } from 'lucide-react'
import { useChatRooms, useCreateChatRoom } from '@/hooks/useChat'
import { ChatRoomList } from '@/components/chat/ChatRoomList'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { NewChatModal } from '@/components/chat/NewChatModal'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { ChatRoom } from '@/types'

export default function ChatPage() {
    // Store the active room ID only — the room object itself is always read
    // from the latest server data so it stays fresh without any effects.
    const [activeRoomId,  setActiveRoomId]  = useState<string | null>(null)
    const [showNewModal,  setShowNewModal]  = useState(false)
    const [mobileView,    setMobileView]    = useState<'list' | 'chat'>('list')

    const { data, isLoading } = useChatRooms()
    const createRoom = useCreateChatRoom()

    const rooms = data?.results ?? []

    // Derive the active room from the latest server data.
    // Auto-select: if nothing is selected yet AND data has arrived, pick the first room
    // and immediately commit its ID to state so this only ever fires once.
    // Using a ref flag instead of a fallback expression avoids re-selecting on every
    // render where activeRoomId happens to still be null (e.g. while typing).
    useEffect(() => {
        if (!activeRoomId && rooms.length > 0) {
            setActiveRoomId(rooms[0].id)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeRoomId, rooms.length])

    const activeRoom: ChatRoom | null = rooms.find(r => r.id === activeRoomId) ?? null

    const handleSelectRoom = (room: ChatRoom) => {
        setActiveRoomId(room.id)
        setMobileView('chat')
    }

    const handleCreateRoom = async (subject: string, orderId?: string) => {
        const room = await createRoom.mutateAsync({ subject, order: orderId })
        setActiveRoomId(room.id)
        setMobileView('chat')
        setShowNewModal(false)
    }

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            {/* Page header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="section-heading">Support Chat</h1>
                    <p className="text-surface-500 text-sm mt-0.5">
                        {data?.count ?? 0} conversation{data?.count !== 1 ? 's' : ''}
                    </p>
                </div>
                <Button onClick={() => setShowNewModal(true)} className="gap-2">
                    <MessageSquarePlus className="h-4 w-4" />
                    New Chat
                </Button>
            </div>

            {/* Main layout */}
            <div className="flex gap-0 rounded-2xl border border-border overflow-hidden bg-white shadow-sm"
                 style={{ height: 'calc(100vh - 220px)', minHeight: 520 }}>

                {/* Sidebar — room list */}
                <div className={cn(
                    'w-full sm:w-80 lg:w-72 xl:w-80 flex-shrink-0 border-r border-border flex flex-col',
                    'sm:flex',
                    mobileView === 'chat' ? 'hidden sm:flex' : 'flex',
                )}>
                    <ChatRoomList
                        rooms={data?.results ?? []}
                        isLoading={isLoading}
                        activeRoomId={activeRoom?.id ?? null}
                        onSelect={handleSelectRoom}
                        onNew={() => setShowNewModal(true)}
                    />
                </div>

                {/* Chat window */}
                <div className={cn(
                    'flex-1 flex flex-col min-w-0',
                    mobileView === 'list' ? 'hidden sm:flex' : 'flex',
                )}>
                    {activeRoom ? (
                        <ChatWindow
                            room={activeRoom}
                            onBack={() => setMobileView('list')}
                            onRoomUpdate={(updated) => setActiveRoomId(updated.id)}
                        />
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center p-8">
                            <div className="h-14 w-14 rounded-2xl bg-brand-50 flex items-center justify-center">
                                <Inbox className="h-7 w-7 text-brand-500" />
                            </div>
                            <div>
                                <p className="font-display font-semibold text-surface-900">No conversation selected</p>
                                <p className="text-sm text-surface-500 mt-1">
                                    Pick one from the left or start a new chat
                                </p>
                            </div>
                            <Button variant="outline" size="sm" onClick={() => setShowNewModal(true)} className="gap-2">
                                <MessageSquarePlus className="h-4 w-4" />
                                Start a conversation
                            </Button>
                        </div>
                    )}
                </div>
            </div>

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