'use client'

import {
    useRef, useEffect, useLayoutEffect, useState, useCallback, useMemo, memo,
    type KeyboardEvent, type ChangeEvent,
} from 'react'
import {
    ArrowLeft, CheckCheck, Send, Loader2,
    CheckCircle2, MoreHorizontal, User,
} from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { useChatRoomWS, useResolveRoom } from '@/hooks/useChat'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu, DropdownMenuContent,
    DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { ChatRoom } from '@/types'
import type { WSChatMessage } from '@/types'

// ─── Typing dots ──────────────────────────────────────────────────────────────

const TypingIndicator = memo(function TypingIndicator({ names }: { names: string[] }) {
    if (!names.length) return null
    return (
        <div className="flex items-center gap-2 px-4 py-2 animate-in fade-in slide-in-from-bottom-1 duration-200">
            <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-surface-100 px-3 py-2.5">
                {[0, 1, 2].map(i => (
                    <span
                        key={i}
                        className="h-1.5 w-1.5 rounded-full bg-surface-400 animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                    />
                ))}
            </div>
            <span className="text-xs text-surface-400 font-mono">
        {names[0]} is typing…
      </span>
        </div>
    )
})

// ─── Date separator ───────────────────────────────────────────────────────────

const DateSeparator = memo(function DateSeparator({ date }: { date: string }) {
    return (
        <div className="flex items-center gap-3 py-3 px-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-[10px] font-mono uppercase tracking-wider text-surface-400 shrink-0">
        {formatDate(date)}
      </span>
            <div className="flex-1 h-px bg-border" />
        </div>
    )
})

// ─── Message bubble ───────────────────────────────────────────────────────────

const MessageBubble = memo(function MessageBubble({
                           msg,
                           showAvatar,
                       }: {
    msg: WSChatMessage
    showAvatar: boolean
}) {
    const isSystem = msg.message_type === 'system'
    const isOwn    = msg.is_own

    if (isSystem) {
        return (
            <div className="flex justify-center py-1">
        <span className="text-[11px] text-surface-400 bg-surface-50 border border-border rounded-full px-3 py-1 font-mono">
          {msg.body}
        </span>
            </div>
        )
    }

    const initials = msg.sender_name
        .split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)

    return (
        <div className={cn(
            'flex items-end gap-2',
            isOwn ? 'flex-row-reverse' : 'flex-row',
            'px-4',
        )}>
            {/* Avatar — always reserves space, only visible when showAvatar */}
            <div className="w-7 shrink-0">
                {!isOwn && showAvatar && (
                    <Avatar className="h-7 w-7">
                        <AvatarFallback className="text-[10px] font-semibold bg-gradient-to-br from-surface-200 to-surface-300 text-surface-600">
                            {initials}
                        </AvatarFallback>
                    </Avatar>
                )}
            </div>

            <div className={cn('flex flex-col gap-1 max-w-[72%] sm:max-w-[60%]', isOwn ? 'items-end' : 'items-start')}>
                {!isOwn && showAvatar && (
                    <span className="text-[11px] font-mono text-surface-400 px-1">
            {msg.sender_name}
          </span>
                )}
                <div className={cn(
                    'px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed break-words shadow-sm',
                    isOwn
                        ? 'bg-gradient-to-br from-brand-500 to-brand-700 text-white rounded-br-sm'
                        : 'bg-surface-100 text-surface-900 rounded-bl-sm',
                )}>
                    {msg.body}
                </div>
                <span className="text-[10px] font-mono px-1 flex items-center gap-1 text-surface-400">
          {new Date(msg.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                    {isOwn && (
                        <CheckCheck className={cn('h-3 w-3', msg.is_read ? 'text-brand-500' : 'text-surface-300')} />
                    )}
        </span>
            </div>
        </div>
    )
})

// ─── Connection status pill ───────────────────────────────────────────────────

function ConnectionPill({ connected, authError }: { connected: boolean; authError: boolean }) {
    if (authError) {
        return (
            <span className="flex items-center gap-1.5 text-[10px] font-mono px-2 py-1 rounded-full text-red-600 bg-red-50">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                Disconnected
            </span>
        )
    }
    return (
        <span className={cn(
            'flex items-center gap-1.5 text-[10px] font-mono px-2 py-1 rounded-full',
            connected
                ? 'text-emerald-600 bg-emerald-50'
                : 'text-amber-600 bg-amber-50 animate-pulse',
        )}>
      <span className={cn('h-1.5 w-1.5 rounded-full', connected ? 'bg-emerald-500' : 'bg-amber-400')} />
            {connected ? 'Live' : 'Connecting…'}
    </span>
    )
}

// ─── Main component ───────────────────────────────────────────────────────────

interface ChatWindowProps {
    room: ChatRoom
    onBack: () => void
    onRoomUpdate: (room: ChatRoom) => void
}

export function ChatWindow({ room, onBack, onRoomUpdate }: ChatWindowProps) {
    const [input, setInput] = useState('')
    const [isTypingLocal, setIsTypingLocal] = useState(false)
    const typingTimer       = useRef<ReturnType<typeof setTimeout> | null>(null)
    const scrollViewportRef = useRef<HTMLDivElement>(null)
    const textareaRef       = useRef<HTMLTextAreaElement>(null)

    const { messages, typers, connected, authError, sendMessage, sendTyping, markRead } =
        useChatRoomWS(room.id)

    const resolveRoom = useResolveRoom()

    const isClosed = room.status === 'resolved' || room.status === 'closed'
    const agentName = room.agent?.full_name || room.agent?.email
    const customerName = room.customer.full_name || room.customer.email
    const customerInitials = customerName.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)

    // Scroll to bottom ONLY when message/typer count increases.
    // We scroll the viewport div directly — scrollIntoView() would scroll the
    // entire page because the document is the nearest scrollable ancestor.
    const prevCountRef = useRef(0)
    const currentCount = messages.length + typers.length
    useLayoutEffect(() => {
        if (currentCount > prevCountRef.current) {
            const el = scrollViewportRef.current
            if (el) el.scrollTop = el.scrollHeight
        }
        prevCountRef.current = currentCount
    }, [currentCount])

    // Mark messages read.
    // The ref is only written inside useLayoutEffect (before the effect below reads
    // it) so we never mutate a ref during render, satisfying react-hooks/refs.
    const markReadRef = useRef(markRead)
    useLayoutEffect(() => {
        markReadRef.current = markRead
    })
    useEffect(() => {
        if (connected && room.unread_count > 0) {
            markReadRef.current()
        }
    }, [connected, room.unread_count])

    // Auto-resize textarea — useLayoutEffect avoids a visible one-frame height flicker.
    useLayoutEffect(() => {
        const ta = textareaRef.current
        if (!ta) return
        ta.style.height = 'auto'
        ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`
    }, [input])

    const handleSend = useCallback(() => {
        const body = input.trim()
        if (!body || isClosed) return
        sendMessage(body)
        setInput('')
        // Stop typing indicator
        sendTyping(false)
        setIsTypingLocal(false)
        if (typingTimer.current) clearTimeout(typingTimer.current)
        textareaRef.current?.focus()
    }, [input, isClosed, sendMessage, sendTyping])

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value)
        if (!isTypingLocal) {
            setIsTypingLocal(true)
            sendTyping(true)
        }
        if (typingTimer.current) clearTimeout(typingTimer.current)
        typingTimer.current = setTimeout(() => {
            setIsTypingLocal(false)
            sendTyping(false)
        }, 2000)
    }

    // Group messages to decide when to show avatars / date separators.
    // Memoized so this only recomputes when the message list itself changes,
    // not on every composer keystroke (which re-renders ChatWindow via `input`).
    const groupedMessages = useMemo(() => messages.reduce<
        Array<{ msg: WSChatMessage; showAvatar: boolean; showDate: boolean }>
    >((acc, msg, i) => {
        const prev = messages[i - 1]
        const showAvatar = !msg.is_own && (
            !prev || prev.sender_email !== msg.sender_email || prev.message_type === 'system'
        )
        const showDate = !prev || (
            new Date(msg.created_at).toDateString() !== new Date(prev.created_at).toDateString()
        )
        acc.push({ msg, showAvatar, showDate })
        return acc
    }, []), [messages])

    return (
        <div className="flex flex-col h-full">
            {/* ── Top bar ─────────────────────────────────────────────────────── */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0 bg-white">
                <div className="flex items-center gap-3">
                    {/* Mobile back button */}
                    <Button
                        variant="ghost" size="icon"
                        className="sm:hidden h-8 w-8 -ml-1"
                        onClick={onBack}
                        aria-label="Back"
                    >
                        <ArrowLeft className="h-4 w-4" />
                    </Button>

                    <Avatar className="h-8 w-8">
                        <AvatarFallback className="text-xs font-semibold bg-gradient-to-br from-brand-400 to-brand-600 text-white">
                            {customerInitials}
                        </AvatarFallback>
                    </Avatar>

                    <div>
                        <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-surface-900 leading-tight">
                {customerName}
              </span>
                            <ConnectionPill connected={connected} authError={authError} />
                        </div>
                        {room.subject && (
                            <p className="text-xs text-surface-500 truncate max-w-[200px] sm:max-w-xs leading-snug">
                                {room.subject}
                            </p>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {agentName && (
                        <div className="hidden sm:flex items-center gap-1.5 text-xs text-surface-500">
                            <User className="h-3.5 w-3.5" />
                            {agentName}
                        </div>
                    )}

                    {!isClosed && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                    onClick={() =>
                                        resolveRoom.mutate(room.id, {
                                            onSuccess: (updated) => onRoomUpdate(updated),
                                        })
                                    }
                                    className="gap-2"
                                >
                                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                                    Mark as resolved
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </div>

            {/* ── Messages ────────────────────────────────────────────────────── */}
            <div ref={scrollViewportRef} className="flex-1 overflow-y-auto bg-surface-50/40">
                <div className="py-4 space-y-1.5">
                    {messages.length === 0 && connected && (
                        <div className="flex flex-col items-center justify-center py-16 gap-2 text-center px-4">
                            <div className="h-11 w-11 rounded-full bg-surface-100 flex items-center justify-center mb-1">
                                <Send className="h-4 w-4 text-surface-400" />
                            </div>
                            <p className="text-sm text-surface-500">No messages yet.</p>
                            <p className="text-xs text-surface-400">
                                {isClosed ? 'This conversation is closed.' : 'Send a message to get started!'}
                            </p>
                        </div>
                    )}

                    {groupedMessages.map(({ msg, showAvatar, showDate }) => (
                        <div key={msg.id} style={{ contentVisibility: 'auto', containIntrinsicSize: '0 56px' }}>
                            {showDate && <DateSeparator date={msg.created_at} />}
                            <MessageBubble msg={msg} showAvatar={showAvatar} />
                        </div>
                    ))}

                    <TypingIndicator names={typers} />
                </div>
            </div>

            {/* ── Input bar ───────────────────────────────────────────────────── */}
            <div className="px-4 py-3 border-t border-border shrink-0 bg-white">
                {authError ? (
                    <div className="flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-50 border border-red-100">
                        <span className="text-sm text-red-600">
                            Connection lost. <button onClick={() => window.location.reload()} className="font-medium underline underline-offset-2">Refresh</button> to reconnect.
                        </span>
                    </div>
                ) : isClosed ? (
                    <div className="flex items-center justify-center gap-2 py-2.5 rounded-xl bg-surface-50 border border-border">
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                        <span className="text-sm text-surface-500">
              This conversation is <span className="font-medium">{room.status}</span>.
            </span>
                    </div>
                ) : (
                    <div className={cn(
                        'flex items-end gap-2 rounded-xl border border-border bg-surface-50 px-3 py-2',
                        'focus-within:border-brand-300 focus-within:ring-2 focus-within:ring-brand-100 transition-all',
                    )}>
            <textarea
                ref={textareaRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Type a message… (Enter to send, Shift+Enter for new line)"
                rows={1}
                className="flex-1 bg-transparent border-none outline-none resize-none text-sm text-surface-900 placeholder:text-surface-400 leading-relaxed py-0.5"
                style={{ maxHeight: 120 }}
            />
                        <Button
                            size="icon"
                            className="h-8 w-8 shrink-0 rounded-lg"
                            onClick={handleSend}
                            disabled={!input.trim() || !connected}
                            aria-label="Send message"
                        >
                            {resolveRoom.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-3.5 w-3.5" />
                            )}
                        </Button>
                    </div>
                )}
            </div>
        </div>
    )
}