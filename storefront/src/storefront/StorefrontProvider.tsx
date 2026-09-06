'use client'

import { createContext, useContext, type ReactNode } from 'react'
import type { Storefront } from '@/types'
import { storefrontFeatures, type StorefrontFeatures } from './config'

type StorefrontContextValue = { storefront: Storefront; features: StorefrontFeatures }
const StorefrontContext = createContext<StorefrontContextValue | null>(null)

export function StorefrontProvider({ storefront, children }: { storefront: Storefront; children: ReactNode }) {
    return (
        <StorefrontContext.Provider value={{ storefront, features: storefrontFeatures(storefront) }}>
            {children}
        </StorefrontContext.Provider>
    )
}

export function useStorefront(): StorefrontContextValue {
    const value = useContext(StorefrontContext)
    if (!value) throw new Error('useStorefront must be used within StorefrontProvider')
    return value
}
