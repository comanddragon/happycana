'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import React, { useState } from 'react'
import axios from 'axios'
import { Toaster } from 'sonner'

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


    return (
        <QueryClientProvider client={queryClient}>
            {children}
            <Toaster
                position="bottom-right"
                richColors
                toastOptions={{
                    style: { borderRadius: '12px', fontSize: '14px' },
                }}
            />
            {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
        </QueryClientProvider>
    )
}