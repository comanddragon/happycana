import { ShoppingBag } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface NavbarCartButtonProps {
    itemCount: number
    mounted: boolean
    onClick: () => void
}

export function NavbarCartButton({ itemCount, mounted, onClick }: NavbarCartButtonProps) {
    return (
        <Button
            variant="ghost"
            size="icon"
            className="relative text-hc-sage hover:bg-hc-paper/10 hover:text-hc-paper"
            onClick={onClick}
            aria-label="Cart"
        >
            <ShoppingBag className="h-4 w-4" />
            {mounted && itemCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-hc-amber text-hc-canopy-2 text-[10px] font-bold flex items-center justify-center">
                    {itemCount > 9 ? '9+' : itemCount}
                </span>
            )}
        </Button>
    )
}
