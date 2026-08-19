import { Search, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface NavbarSearchProps {
    search: string
    setSearch: (value: string) => void
    searchOpen: boolean
    setSearchOpen: (open: boolean) => void
    onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void
}

export function NavbarSearch({ search, setSearch, searchOpen, setSearchOpen, onKeyDown }: NavbarSearchProps) {
    return (
        <div className={cn('hidden md:flex items-center transition-all duration-200', searchOpen ? 'flex-1 max-w-sm' : '')}>
            {searchOpen ? (
                <div className="flex items-center gap-2 w-full">
                    <Input
                        autoFocus
                        placeholder="Search the menu…"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        onKeyDown={onKeyDown}
                        className="border-hc-paper/20 bg-hc-paper/[0.06] text-hc-paper placeholder:text-hc-sage-dim focus-visible:ring-hc-amber-light/40"
                    />
                    <Button
                        variant="ghost"
                        size="icon"
                        className="text-hc-sage hover:bg-hc-paper/10 hover:text-hc-paper"
                        onClick={() => { setSearchOpen(false); setSearch('') }}
                    >
                        <X className="h-4 w-4" />
                    </Button>
                </div>
            ) : (
                <Button
                    variant="ghost"
                    size="icon"
                    className="text-hc-sage hover:bg-hc-paper/10 hover:text-hc-paper"
                    onClick={() => setSearchOpen(true)}
                    aria-label="Search"
                >
                    <Search className="h-4 w-4" />
                </Button>
            )}
        </div>
    )
}
