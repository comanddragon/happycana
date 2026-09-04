import { describe, it, expect, beforeEach } from 'vitest'
import { useCartStore } from '../cart'
import type { Cart } from '@/types'

const makeCart = (overrides: Partial<Cart> = {}): Cart => ({
    id: 'cart-1',
    items: [],
    item_count: 3,
    total_price: '42.50',
    updated_at: new Date().toISOString(),
    ...overrides,
})

describe('useCartStore', () => {
    beforeEach(() => {
        useCartStore.setState({ cart: null, isOpen: false })
    })

    it('starts with no cart and closed drawer', () => {
        const state = useCartStore.getState()
        expect(state.cart).toBeNull()
        expect(state.isOpen).toBe(false)
    })

    it('setCart stores the cart', () => {
        const cart = makeCart()
        useCartStore.getState().setCart(cart)
        expect(useCartStore.getState().cart).toEqual(cart)
    })

    it('itemCount reflects the cart, defaulting to 0 when empty', () => {
        expect(useCartStore.getState().itemCount()).toBe(0)
        useCartStore.getState().setCart(makeCart({ item_count: 5 }))
        expect(useCartStore.getState().itemCount()).toBe(5)
    })

    it('subtotal reflects the cart, defaulting to "0.00" when empty', () => {
        expect(useCartStore.getState().subtotal()).toBe('0.00')
        useCartStore.getState().setCart(makeCart({ total_price: '19.99' }))
        expect(useCartStore.getState().subtotal()).toBe('19.99')
    })

    it('openCart / closeCart toggle isOpen explicitly', () => {
        useCartStore.getState().openCart()
        expect(useCartStore.getState().isOpen).toBe(true)
        useCartStore.getState().closeCart()
        expect(useCartStore.getState().isOpen).toBe(false)
    })

    it('toggleCart flips isOpen from its current value', () => {
        expect(useCartStore.getState().isOpen).toBe(false)
        useCartStore.getState().toggleCart()
        expect(useCartStore.getState().isOpen).toBe(true)
        useCartStore.getState().toggleCart()
        expect(useCartStore.getState().isOpen).toBe(false)
    })

    it('setCart(null) clears the cart back to defaults', () => {
        useCartStore.getState().setCart(makeCart())
        useCartStore.getState().setCart(null)
        expect(useCartStore.getState().cart).toBeNull()
        expect(useCartStore.getState().itemCount()).toBe(0)
    })
})