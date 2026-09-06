import { Bell } from 'lucide-react'
import { cn, formatRelativeDate } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
    DropdownMenu, DropdownMenuContent, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useNotifications, useMarkNotificationRead } from '@/hooks/useApi'

type Notification = NonNullable<ReturnType<typeof useNotifications>['data']>['results'][number]
type MarkReadId = Parameters<ReturnType<typeof useMarkNotificationRead>['mutate']>[0]

interface NavbarNotificationsProps {
    notifications: Notification[] | undefined
    unread: number
    onMarkRead: (id: MarkReadId) => void
}

export function NavbarNotifications({ notifications, unread, onMarkRead }: NavbarNotificationsProps) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative text-hc-sage hover:bg-hc-paper/10 hover:text-hc-paper" aria-label="Notifications">
                    <Bell className="h-4 w-4" />
                    {unread > 0 && (
                        <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-hc-amber-light ring-2 ring-hc-canopy" />
                    )}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 p-0">
                <div className="flex items-center justify-between px-4 py-3 border-b">
                    <span className="text-sm font-medium">Notifications</span>
                    {unread > 0 && <Badge variant="secondary">{unread} new</Badge>}
                </div>
                <ScrollArea className="max-h-80">
                    {!notifications?.length && (
                        <p className="p-4 text-sm text-muted-foreground text-center">No notifications</p>
                    )}
                    {notifications?.slice(0, 8).map(n => (
                        <button
                            key={n.id}
                            onClick={() => onMarkRead(n.id)}
                            className={cn(
                                'w-full text-left px-4 py-3 hover:bg-muted transition-colors border-b last:border-0',
                                !n.is_read && 'bg-hc-amber-light/10',
                            )}
                        >
                            <div className="flex gap-3">
                                {!n.is_read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-hc-amber" />}
                                <div className={cn(!n.is_read ? '' : 'ml-5')}>
                                    <p className="text-sm font-medium">{n.title}</p>
                                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{n.body}</p>
                                    <p className="text-xs text-muted-foreground/60 mt-1">{formatRelativeDate(n.created_at)}</p>
                                </div>
                            </div>
                        </button>
                    ))}
                </ScrollArea>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
