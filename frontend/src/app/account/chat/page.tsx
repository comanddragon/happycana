'use client'

import {useState} from 'react'
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

    // Derive the active room straight from render — no effect needed.
    // Nothing selected yet → default to the first room once data has
    // arrived. Once the visitor picks one, activeRoomId is set and this
    // stops falling back, even if that room later drops out of `rooms`.
    const activeRoom: ChatRoom | null =
        (activeRoomId ? rooms.find(r => r.id === activeRoomId) : rooms[0]) ?? null

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