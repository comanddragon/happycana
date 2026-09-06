'use client'

import { memo } from 'react'
import { MessageSquarePlus, Inbox } from 'lucide-react'
import { cn, formatRelativeDate } from '@/lib/utils'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import type { ChatRoom, ChatRoomStatus } from '@/types'

// ─── Status badge ─────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<ChatRoomStatus, string> = {
    open:     'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
    assigned: 'bg-brand-50 text-brand-700 ring-1 ring-brand-200',
    resolved: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
    closed:   'bg-surface-100 text-surface-500 ring-1 ring-surface-200',
}

function StatusBadge({ status }: { status: ChatRoomStatus }) {
    return (
        <span className={cn('text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full', STATUS_STYLES[status])}>
      {status}
    </span>
    )
}

// ─── Single room row ──────────────────────────────────────────────────────────

const RoomRow = memo(function RoomRow({
                     room,
                     isActive,
                     onSelect,
                 }: {
    room: ChatRoom
    isActive: boolean
    onSelect: (room: ChatRoom) => void
}) {
    const name     = room.customer.full_name || room.customer.email
    const initials = name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
    const preview  = room.latest_message?.body ?? 'No messages yet'

    return (
        <button
            onClick={() => onSelect(room)}
            className={cn(
                'w-full text-left px-3 py-3 rounded-xl transition-colors duration-150 group',
                isActive
                    ? 'bg-brand-50 ring-1 ring-brand-100'
                    : 'hover:bg-surface-50',
            )}
        >
            <div className="flex items-start gap-3">
                <Avatar className="h-9 w-9 shrink-0">
                    <AvatarFallback className={cn(
                        'text-xs font-semibold',
                        isActive
                            ? 'bg-gradient-to-br from-brand-400 to-brand-600 text-white'
                            : 'bg-gradient-to-br from-surface-200 to-surface-300 text-surface-600',
                    )}>
                        {initials}
                    </AvatarFallback>
                </Avatar>

                <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
            <span className={cn(
                'text-sm font-medium truncate',
                isActive ? 'text-brand-700' : 'text-surface-900',
            )}>
              {name}
            </span>
                        <span className="text-[10px] text-surface-400 shrink-0 font-mono">
              {formatRelativeDate(room.updated_at)}
            </span>
                    </div>

                    <p className="text-xs text-surface-500 truncate mt-0.5 leading-snug">
                        {room.subject || preview}
                    </p>

                    <div className="flex items-center justify-between mt-1.5">
                        <StatusBadge status={room.status} />
                        {room.unread_count > 0 && (
                            <span className="h-5 min-w-5 px-1.5 rounded-full bg-brand-600 text-white text-[10px] font-bold flex items-center justify-center tabular-nums">
                {room.unread_count > 9 ? '9+' : room.unread_count}
              </span>
                        )}
                    </div>
                </div>
            </div>
        </button>
    )
})

// ─── Room list ────────────────────────────────────────────────────────────────

interface ChatRoomListProps {
    rooms: ChatRoom[]
    isLoading: boolean
    activeRoomId: string | null
    onSelect: (room: ChatRoom) => void
    onNew: () => void
}

export function ChatRoomList({ rooms, isLoading, activeRoomId, onSelect, onNew }: ChatRoomListProps) {
    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
                <span className="text-sm font-semibold text-surface-900">Conversations</span>
                <Button variant="ghost" size="icon" onClick={onNew} className="h-7 w-7" aria-label="New chat">
                    <MessageSquarePlus className="h-4 w-4" />
                </Button>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
                {isLoading ? (
                    Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="flex items-start gap-3 px-3 py-3">
                            <Skeleton className="h-9 w-9 rounded-full shrink-0" />
                            <div className="flex-1 space-y-2">
                                <Skeleton className="h-3.5 w-3/4" />
                                <Skeleton className="h-3 w-1/2" />
                            </div>
                        </div>
                    ))
                ) : rooms.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-14 text-center gap-3 px-4">
                        <div className="h-12 w-12 rounded-full bg-surface-100 flex items-center justify-center">
                            <Inbox className="h-5 w-5 text-surface-400" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-surface-900">No conversations yet</p>
                            <p className="text-xs text-surface-400 mt-0.5">Start one to talk with our support team</p>
                        </div>
                        <Button variant="outline" size="sm" onClick={onNew} className="gap-1.5 mt-1">
                            <MessageSquarePlus className="h-3.5 w-3.5" />
                            Start one
                        </Button>
                    </div>
                ) : (
                    rooms.map(room => (
                        <RoomRow
                            key={room.id}
                            room={room}
                            isActive={room.id === activeRoomId}
                            onSelect={onSelect}
                        />
                    ))
                )}
            </div>
        </div>
    )
}