// store/cart.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Cart } from '@/types'

interface CartState {
    cart: Cart | null
    isOpen: boolean
    setCart: (cart: Cart | null) => void
    openCart: () => void
    closeCart: () => void
    toggleCart: () => void
    itemCount: () => number
    subtotal: () => string
}

export const useCartStore = create<CartState>()(
    persist(
        (set, get) => ({
            cart: null,
            isOpen: false,
            setCart: (cart) => set({ cart }),
            openCart: () => set({ isOpen: true }),
            closeCart: () => set({ isOpen: false }),
            toggleCart: () => set(s => ({ isOpen: !s.isOpen })),
            itemCount: () => get().cart?.item_count ?? 0,
            subtotal: () => get().cart?.total_price ?? '0.00',
        }),
        {
            name: 'cart-store',
            partialize: (s) => ({ cart: s.cart }),
        }
    )
)