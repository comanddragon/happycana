// store/auth.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { clearTokens } from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  /** True once `user` is a passwordless guest session — kept separate from
   *  isAuthenticated so guest UI can still gate on it without every caller
   *  re-deriving `user?.is_guest`. */
  isGuest: boolean
  setUser: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isGuest: false,
      setUser: (user) => set({ user, isAuthenticated: !!user, isGuest: !!user?.is_guest }),
      logout: () => {
        clearTokens()
        set({ user: null, isAuthenticated: false, isGuest: false })
      },
    }),
    { name: 'auth-store' }
  )
)
