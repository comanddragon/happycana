// lib/guestSession.ts
// Lazily issues a passwordless guest identity the first time an
// unauthenticated visitor needs one — adding to cart, opening the chat
// widget, or reaching the checkout contact step. Safe to call repeatedly;
// once a session exists (guest or real) this is a no-op.

import { authService, userService } from './services'
import { useAuthStore } from '@/store/auth'
import { getAccessToken, getRefreshToken } from '@/lib/api'

let restorePromise: Promise<ReturnType<typeof useAuthStore.getState>['user']> | null = null

/** Restore the persisted JWT identity after a browser/app restart. */
export function restoreExistingSession() {
    const { user, isAuthenticated, setUser } = useAuthStore.getState()
    const hasToken = Boolean(getAccessToken() || getRefreshToken())

    if (user && isAuthenticated && hasToken) return Promise.resolve(user)
    if (!hasToken) return Promise.resolve(null)
    if (restorePromise) return restorePromise

    restorePromise = userService.me()
        .then(restoredUser => {
            setUser(restoredUser)
            return restoredUser
        })
        .catch(() => {
            setUser(null)
            return null
        })
        .finally(() => {
            restorePromise = null
        })

    return restorePromise
}

/**
 * Ensures the visitor has a JWT session, creating a guest one if needed.
 * Returns the current (or newly created) user.
 */
export async function ensureGuestSession(email?: string) {
    const { setUser } = useAuthStore.getState()
    let { isAuthenticated, user } = useAuthStore.getState()

    if (!user && (getAccessToken() || getRefreshToken())) {
        user = await restoreExistingSession()
        isAuthenticated = Boolean(user)
    }

    if (isAuthenticated && user && (getAccessToken() || getRefreshToken())) {
        // Already a real or guest session — nothing to do unless we're
        // attaching an email to an existing guest for the first time.
        if (user.is_guest && email && user.email !== email) {
            const { user: updated } = await authService.guestSession(email)
            setUser(updated)
            return updated
        }
        return user
    }

    if (isAuthenticated || user) setUser(null)

    const { user: guestUser } = await authService.guestSession(email)
    setUser(guestUser)
    return guestUser
}
