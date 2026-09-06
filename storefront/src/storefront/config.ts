import type { Storefront } from '@/types'

export type StorefrontKind = 'general' | 'dispensary' | 'hash' | 'peptides' | 'footwear'

export interface StorefrontFeatures {
    ageGate: boolean
    cannabisCatalog: boolean
    labResults: boolean
    footwearCatalog: boolean
    peptideCatalog: boolean
}

const FEATURES: Record<StorefrontKind, StorefrontFeatures> = {
    general: { ageGate: false, cannabisCatalog: false, labResults: false, footwearCatalog: false, peptideCatalog: false },
    dispensary: { ageGate: true, cannabisCatalog: true, labResults: true, footwearCatalog: false, peptideCatalog: false },
    hash: { ageGate: true, cannabisCatalog: true, labResults: true, footwearCatalog: false, peptideCatalog: false },
    peptides: { ageGate: false, cannabisCatalog: false, labResults: true, footwearCatalog: false, peptideCatalog: true },
    footwear: { ageGate: false, cannabisCatalog: false, labResults: false, footwearCatalog: true, peptideCatalog: false },
}

export function storefrontFeatures(storefront: Storefront): StorefrontFeatures {
    return FEATURES[storefront.kind as StorefrontKind] ?? FEATURES.general
}

export function brandingString(storefront: Storefront, key: string): string | undefined {
    const value = storefront.branding?.[key]
    return typeof value === 'string' && value.trim() ? value.trim() : undefined
}
