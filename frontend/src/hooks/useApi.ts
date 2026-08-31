// hooks/useApi.ts
import {
    useQuery, useMutation, useQueryClient,
} from '@tanstack/react-query'
import { toast } from 'sonner'
import {
    catalogService, cartService, orderService,
    notificationService, checkoutService, userService,
} from '@/lib/services'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import { extractErrorMessage } from '@/lib/api'
import { ensureGuestSession } from '@/lib/guestSession'
import { qk } from '@/lib/queryKeys'
import type {
    ProductFilterParams,
} from '@/types'

// ─── Query Keys ───────────────────────────────────────────────────────────────
// Re-exported from lib/queryKeys so existing imports of `qk` from this file
// keep working; the canonical definition lives there so it can also be
// imported from Server Components for prefetch/hydration.
export { qk }

// ─── Catalog ──────────────────────────────────────────────────────────────────

export function useProducts(params?: ProductFilterParams) {
    return useQuery({
        queryKey: qk.products(params),
        queryFn:  () => catalogService.listProducts(params),
        staleTime: 60_000,
    })
}

export function useProduct(slug: string) {
    return useQuery({
        queryKey: qk.product(slug),
        queryFn:  () => catalogService.getProduct(slug),
        enabled:  !!slug,
        staleTime: 60_000,
    })
}

export function useCategories() {
    return useQuery({
        queryKey: qk.categories(),
        queryFn: async () => {
            const result = await catalogService.listCategories()
            // Ensure we always return an array even if the API shape changes
            return Array.isArray(result) ? result : []
        },
        staleTime: 300_000,
    })
}

// Requires backend_patch/api_patch.py's Brand endpoints.
export function useBrands() {
    return useQuery({
        queryKey: qk.brands(),
        queryFn:  catalogService.listBrands,
        staleTime: 300_000,
    })
}

export function useBrand(slug: string) {
    return useQuery({
        queryKey: qk.brand(slug),
        queryFn:  () => catalogService.getBrand(slug),
        enabled:  !!slug,
        staleTime: 300_000,
    })
}

// Requires the EffectListView addendum in the backend patch notes.
export function useEffects() {
    return useQuery({
        queryKey: qk.effects(),
        queryFn:  catalogService.listEffects,
        staleTime: 300_000,
    })
}

// ─── Cart ─────────────────────────────────────────────────────────────────────

export function useCart() {
    const setCart = useCartStore(s => s.setCart)
    const isAuthenticated = useAuthStore(s => s.isAuthenticated)
    return useQuery({
        queryKey: qk.cart(),
        queryFn: async () => {
            const cart = await cartService.getCart()
            setCart(cart)
            return cart
        },
        enabled: isAuthenticated,
        staleTime: 30_000,
    })
}

export function useAddToCart() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: async ({ variant, quantity }: { variant: string; quantity: number }) => {
            // Cart endpoints require auth — bootstrap a guest session first
            // if this visitor doesn't have one yet. No-op once they do.
            await ensureGuestSession()
            return cartService.addItem(variant, quantity)
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: qk.cart() })
            toast.success('Added to cart')
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

export function useUpdateCartItem() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: ({ id, quantity }: { id: string; quantity: number }) =>
            cartService.updateItem(id, quantity),
        onSuccess: () => qc.invalidateQueries({ queryKey: qk.cart() }),
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

export function useRemoveCartItem() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (id: string) => cartService.removeItem(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: qk.cart() }),
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

// ─── Orders ───────────────────────────────────────────────────────────────────

export function useOrders(params?: Record<string, string>) {
    return useQuery({
        queryKey: qk.orders(params),
        queryFn:  () => orderService.list(params),
    })
}

export function useOrder(id: string) {
    return useQuery({
        queryKey: qk.order(id),
        queryFn:  () => orderService.get(id),
        enabled:  !!id,
    })
}

export function useCancelOrder() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (id: string) => orderService.cancel(id),
        onSuccess: (_, id) => {
            qc.invalidateQueries({ queryKey: qk.orders() })
            qc.invalidateQueries({ queryKey: qk.order(id) })
            toast.success('Order cancelled')
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

// ─── Checkout ─────────────────────────────────────────────────────────────────

export function useShippingMethods() {
    return useQuery({
        queryKey: qk.shipping(),
        queryFn:  checkoutService.listShippingMethods,
        staleTime: 300_000,
    })
}

export function useValidateCoupon() {
    return useMutation({
        mutationFn: ({ code, subtotal }: { code: string; subtotal: string }) =>
            checkoutService.validateCoupon(code, subtotal),
    })
}

export function useCheckout() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: checkoutService.checkout,
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: qk.cart() })
            qc.invalidateQueries({ queryKey: qk.orders() })
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

// ─── User ─────────────────────────────────────────────────────────────────────

export function useMe() {
    return useQuery({
        queryKey: qk.me(),
        queryFn:  userService.me,
        staleTime: 120_000,
    })
}

export function useAddresses() {
    return useQuery({
        queryKey: qk.addresses(),
        queryFn:  userService.listAddresses,
    })
}

export function useCreateAddress() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: userService.createAddress,
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: qk.addresses() })
            toast.success('Address saved')
        },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })
}

export function useDeleteAddress() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: userService.deleteAddress,
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: qk.addresses() })
            toast.success('Address removed')
        },
    })
}

// ─── Notifications ────────────────────────────────────────────────────────────

export function useNotifications() {
    const isAuthenticated = useAuthStore(s => s.isAuthenticated)
    return useQuery({
        queryKey: qk.notifications(),
        queryFn:  notificationService.list,
        enabled: isAuthenticated,
        refetchInterval: 30_000,
    })
}

export function useMarkNotificationRead() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (id: string) => notificationService.markRead(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: qk.notifications() }),
    })
}