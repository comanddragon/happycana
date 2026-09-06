// lib/guestSession.ts
// Lazily issues a passwordless guest identity the first time an
// unauthenticated visitor needs one — adding to cart, opening the chat
// widget, or reaching the checkout contact step. Safe to call repeatedly;
// once a session exists (guest or real) this is a no-op.

import { authService } from './services'
import { useAuthStore } from '@/store/auth'

/**
 * Ensures the visitor has a JWT session, creating a guest one if needed.
 * Returns the current (or newly created) user.
 */
export async function ensureGuestSession(email?: string) {
    const { isAuthenticated, user, setUser } = useAuthStore.getState()

    if (isAuthenticated && user) {
        // Already a real or guest session — nothing to do unless we're
        // attaching an email to an existing guest for the first time.
        if (user.is_guest && email && user.email !== email) {
            const { user: updated } = await authService.guestSession(email)
            setUser(updated)
            return updated
        }
        return user
    }

    const { user: guestUser } = await authService.guestSession(email)
    setUser(guestUser)
    return guestUser
}
