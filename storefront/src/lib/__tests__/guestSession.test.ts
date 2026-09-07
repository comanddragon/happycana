import { beforeEach, describe, expect, it, vi } from 'vitest'

import { restoreExistingSession } from '@/lib/guestSession'
import { userService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'

vi.mock('@/lib/api', () => ({
    getAccessToken: vi.fn(() => 'access-token'),
    getRefreshToken: vi.fn(() => 'refresh-token'),
    clearTokens: vi.fn(),
    setTokens: vi.fn(),
    api: {},
}))

describe('restoreExistingSession', () => {
    beforeEach(() => {
        useAuthStore.setState({ user: null, isAuthenticated: false, isGuest: false })
        vi.restoreAllMocks()
    })

    it('hydrates a guest user when tokens survived but persisted auth is empty', async () => {
        const guest = {
            id: 'guest-1',
            email: 'guest@example.com',
            first_name: '',
            last_name: '',
            phone: '',
            is_guest: true,
            is_active: true,
            is_staff: false,
            created_at: '2026-09-07T00:00:00Z',
            updated_at: '2026-09-07T00:00:00Z',
        }
        vi.spyOn(userService, 'me').mockResolvedValue(guest)

        await restoreExistingSession()

        expect(useAuthStore.getState()).toMatchObject({
            user: guest,
            isAuthenticated: true,
            isGuest: true,
        })
    })
})
