'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Toaster } from 'sonner'
import { useAuthStore } from '@/store/auth'
import { restoreExistingSession } from '@/lib/guestSession'

export function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        staleTime: 30_000,
                        gcTime: 5 * 60_000,
                        retry: (failureCount, error) => {
                            if (axios.isAxiosError(error)) {
                                if (error.response?.status === 401) return false
                                if (error.response?.status === 404) return false
                            }
                            return failureCount < 2
                        },
                    },
                },
            })
    )

    useEffect(() => {
        void restoreExistingSession()

        const expire = () => {
            useAuthStore.getState().setUser(null)
            queryClient.removeQueries({ queryKey: ['cart'] })
            queryClient.removeQueries({ queryKey: ['notifications'] })
        }
        window.addEventListener('auth-session-expired', expire)
        return () => window.removeEventListener('auth-session-expired', expire)
    }, [queryClient])


    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <Toaster
                position="bottom-left"
                richColors
                toastOptions={{
                    style: { borderRadius: '12px', fontSize: '14px' },
                }}
            />
            {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
        </QueryClientProvider>
    )
}
