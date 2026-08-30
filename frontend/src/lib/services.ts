// lib/services.ts
// One service per Django app, matching the backend's URL patterns exactly.

import { api, setTokens, clearTokens } from './api'
import type { ChatRoom, ChatMessage } from '@/types'
import type {
    User, Address, LoginResponse, RegisterResponse,
    Category, Product, ProductVariant, PaginatedResponse,
    Cart, CartItem, Order, Payment, ShippingMethod, Shipment,
    CouponValidationResult, Notification, CheckoutPayload, CheckoutResult,
    Brand, Effect, ProductFilterParams,
} from '@/types'

/** Django's StandardResultsPagination wraps list responses in { results: [] }.
 *  Some views may also return plain arrays. This helper handles both. */
function unwrapList<T>(data: T[] | { results: T[] }): T[] {
    return Array.isArray(data) ? data : (data as { results: T[] }).results ?? []
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authService = {
    async login(email: string, password: string): Promise<LoginResponse> {
        const { data } = await api.post<LoginResponse>('/auth/login/', { email, password })
        setTokens(data.access, data.refresh)
        return data
    },

    async register(payload: {
        email: string; password: string; password2: string; first_name?: string; last_name?: string
    }): Promise<RegisterResponse> {
        const { data } = await api.post<RegisterResponse>('/auth/register/', payload)
        setTokens(data.access, data.refresh)
        return data
    },

    async logout(refresh: string): Promise<void> {
        await api.post('/auth/logout/', { refresh })
        clearTokens()
    },

    /** Passwordless guest identity — used for guest checkout and guest chat. */
    async guestSession(email?: string): Promise<RegisterResponse> {
        const { data } = await api.post<RegisterResponse>('/auth/guest/', email ? { email } : {})
        setTokens(data.access, data.refresh)
        return data
    },
}

// ─── Users ────────────────────────────────────────────────────────────────────

export const userService = {
    async me(): Promise<User> {
        const { data } = await api.get<User>('/users/me/')
        return data
    },

    async update(payload: Partial<User>): Promise<User> {
        const { data } = await api.patch<User>('/users/me/', payload)
        return data
    },

    async changePassword(old_password: string, new_password: string): Promise<void> {
        await api.put('/users/me/password/', { old_password, new_password })
    },

    // Addresses
    async listAddresses(): Promise<Address[]> {
        const { data } = await api.get('/users/me/addresses/')
        return unwrapList<Address>(data)
    },

    async createAddress(payload: Omit<Address, 'id' | 'user'>): Promise<Address> {
        const { data } = await api.post<Address>('/users/me/addresses/', payload)
        return data
    },

    async updateAddress(id: string, payload: Partial<Address>): Promise<Address> {
        const { data } = await api.patch<Address>(`/users/me/addresses/${id}/`, payload)
        return data
    },

    async deleteAddress(id: string): Promise<void> {
        await api.delete(`/users/me/addresses/${id}/`)
    },
}

// ─── Catalog ──────────────────────────────────────────────────────────────────

export const catalogService = {
    async listCategories(params?: Record<string, string>): Promise<Category[]> {
        const { data } = await api.get('/catalog/categories/', { params })
        return unwrapList<Category>(data)
    },

    async getCategory(slug: string): Promise<Category> {
        const { data } = await api.get<Category>(`/catalog/categories/${slug}/`)
        return data
    },

    async listProducts(params?: ProductFilterParams): Promise<PaginatedResponse<Product>> {
        const { data } = await api.get<PaginatedResponse<Product>>('/catalog/products/', { params })
        return data
    },

    async getProduct(slug: string): Promise<Product> {
        const { data } = await api.get<Product>(`/catalog/products/${slug}/`)
        return data
    },

    async getVariant(id: string): Promise<ProductVariant> {
        const { data } = await api.get<ProductVariant>(`/catalog/variants/${id}/`)
        return data
    },

    // Requires backend_patch/api_patch.py's BrandListView/BrandDetailView.
    // Matches the /catalog/brands/ endpoints proposed there.
    async listBrands(): Promise<Brand[]> {
        const { data } = await api.get('/catalog/brands/')
        return unwrapList<Brand>(data)
    },

    async getBrand(slug: string): Promise<Brand> {
        const { data } = await api.get<Brand>(`/catalog/brands/${slug}/`)
        return data
    },

    // Requires the EffectListView addendum below. Powers the "shop by
    // effect" filter — the fixed list of effect tags, not a per-product one.
    async listEffects(): Promise<Effect[]> {
        const { data } = await api.get('/catalog/effects/')
        return unwrapList<Effect>(data)
    },
}

// ─── Cart ─────────────────────────────────────────────────────────────────────

export const cartService = {
    async getCart(): Promise<Cart> {
        const { data } = await api.get<Cart>('/orders/cart/')
        return data
    },

    async addItem(variant: string, quantity: number): Promise<CartItem> {
        const { data } = await api.post<CartItem>('/orders/cart/items/', { variant, quantity })
        return data
    },

    async updateItem(item_id: string, quantity: number): Promise<CartItem> {
        const { data } = await api.patch<CartItem>(`/orders/cart/items/${item_id}/`, { quantity })
        return data
    },

    async removeItem(item_id: string): Promise<void> {
        await api.delete(`/orders/cart/items/${item_id}/`)
    },

    async clearCart(): Promise<void> {
        await api.delete('/orders/cart/')
    },
}

// ─── Orders ───────────────────────────────────────────────────────────────────

export const orderService = {
    async list(params?: Record<string, string>): Promise<PaginatedResponse<Order>> {
        const { data } = await api.get<PaginatedResponse<Order>>('/orders/', { params })
        return data
    },

    async get(id: string): Promise<Order> {
        const { data } = await api.get<Order>(`/orders/${id}/`)
        return data
    },

    async cancel(id: string): Promise<Order> {
        const { data } = await api.post<Order>(`/orders/${id}/cancel/`)
        return data
    },
}

// ─── Checkout ─────────────────────────────────────────────────────────────────

export const checkoutService = {
    async checkout(payload: CheckoutPayload): Promise<CheckoutResult> {
        // NOTE: the real endpoint is /orders/checkout/ (OrderCreateView) —
        // /checkout/ doesn't exist and this call has never actually worked.
        const { data } = await api.post<CheckoutResult>('/orders/checkout/', payload)
        return data
    },

    async validateCoupon(code: string, subtotal: string): Promise<CouponValidationResult> {
        const { data } = await api.post<CouponValidationResult>('/promotions/coupons/validate/', {
            code,
            subtotal,
        })
        return data
    },

    async listShippingMethods(): Promise<ShippingMethod[]> {
        const { data } = await api.get('/shipping/methods/')
        return unwrapList<ShippingMethod>(data)
    },
}

// ─── Payments ─────────────────────────────────────────────────────────────────

export const paymentService = {
    async list(): Promise<PaginatedResponse<Payment>> {
        const { data } = await api.get<PaginatedResponse<Payment>>('/payments/')
        return data
    },

    async get(id: string): Promise<Payment> {
        const { data } = await api.get<Payment>(`/payments/${id}/`)
        return data
    },
}

// ─── Shipping ─────────────────────────────────────────────────────────────────

export const shippingService = {
    async getShipment(orderId: string): Promise<Shipment> {
        const { data } = await api.get<Shipment>(`/shipping/shipments/?order=${orderId}`)
        return data
    },
}

// ─── Notifications ────────────────────────────────────────────────────────────

export const notificationService = {
    async list(): Promise<PaginatedResponse<Notification>> {
        const { data } = await api.get<PaginatedResponse<Notification>>('/notifications/')
        return data
    },

    async markRead(id: string): Promise<void> {
        await api.post('/notifications/mark-read/', { ids: [id] })
    },

    async markAllRead(): Promise<void> {
        await api.post('/notifications/mark-all-read/')
    },
}

// lib/chatService.ts
// Follows the exact same pattern as services.ts



export const chatService = {
    // ── Rooms ──────────────────────────────────────────────────────────────────

    async listRooms(params?: { status?: string }): Promise<PaginatedResponse<ChatRoom>> {
        const { data } = await api.get<PaginatedResponse<ChatRoom>>('/chat/rooms/', { params })
        return data
    },

    async getRoom(id: string): Promise<ChatRoom> {
        const { data } = await api.get<ChatRoom>(`/chat/rooms/${id}/`)
        return data
    },

    async createRoom(payload: { subject: string; order?: string }): Promise<ChatRoom> {
        const { data } = await api.post<ChatRoom>('/chat/rooms/', payload)
        return data
    },

    async resolveRoom(id: string): Promise<ChatRoom> {
        const { data } = await api.post<ChatRoom>(`/chat/rooms/${id}/resolve/`)
        return data
    },

    async assignAgent(id: string, agent_id: string): Promise<ChatRoom> {
        const { data } = await api.post<ChatRoom>(`/chat/rooms/${id}/assign/`, { agent_id })
        return data
    },

    // ── Messages ───────────────────────────────────────────────────────────────

    async listMessages(roomId: string): Promise<ChatMessage[]> {
        const { data } = await api.get<ChatMessage[]>(`/chat/rooms/${roomId}/messages/`)
        return data
    },

    async sendMessage(roomId: string, body: string, message_type = 'text'): Promise<ChatMessage> {
        const { data } = await api.post<ChatMessage>(`/chat/rooms/${roomId}/messages/`, {
            body,
            message_type,
        })
        return data
    },
}