// store/auth.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { clearTokens } from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => {
        clearTokens()
        set({ user: null, isAuthenticated: false })
      },
    }),
    { name: 'auth-store' }
  )
)
