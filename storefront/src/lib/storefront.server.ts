import { timedFetch } from './timedFetch.server'
import type { Storefront } from '@/types'
import { cache } from 'react'

export const getStorefront = cache(async (): Promise<Storefront> => {
    const response = await timedFetch(`${process.env.API_URL}/storefront/`, {
        next: { revalidate: 3600 },
    })
    if (!response.ok) throw new Error(`Failed to resolve storefront: ${response.status}`)
    return response.json()
})
