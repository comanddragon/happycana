import type { StorefrontKind } from './config'

export interface StorefrontTheme {
    colors: {
        canopy: string
        canopy2: string
        canopy3: string
        amber: string
        amberLight: string
        amberDim: string
        sage: string
        sageDim: string
        paper: string
        paper2: string
        ink: string
        inkSoft: string
    }
    radius: string
    fonts: {
        display: 'fraunces' | 'peptideDisplay'
        body: 'spaceGrotesk'
        mono: 'ibmPlexMono'
    }
    productCardVariant: 'organic' | 'clinical'
}

const DISPENSARY_THEME: StorefrontTheme = {
    colors: {
        canopy: '#172319',
        canopy2: '#0e1611',
        canopy3: '#223023',
        amber: '#c8792e',
        amberLight: '#eab767',
        amberDim: '#8a5424',
        sage: '#9bae8d',
        sageDim: '#6d7f63',
        paper: '#f8f3f0',
        paper2: '#ece3d1',
        ink: '#17140f',
        inkSoft: '#4a453c',
    },
    radius: '0.625rem',
    fonts: { display: 'fraunces', body: 'spaceGrotesk', mono: 'ibmPlexMono' },
    productCardVariant: 'organic',
}

export const STOREFRONT_THEMES: Record<StorefrontKind, StorefrontTheme> = {
    general: DISPENSARY_THEME,
    dispensary: DISPENSARY_THEME,
    hash: {
        colors: {
            canopy: '#1b1510',
            canopy2: '#0d0a08',
            canopy3: '#38291b',
            amber: '#d9962f',
            amberLight: '#f3c86e',
            amberDim: '#98601d',
            sage: '#c9b99b',
            sageDim: '#8d7b61',
            paper: '#f5f0e6',
            paper2: '#e8dcc5',
            ink: '#21170d',
            inkSoft: '#655746',
        },
        radius: '0.5rem',
        fonts: { display: 'fraunces', body: 'spaceGrotesk', mono: 'ibmPlexMono' },
        productCardVariant: 'organic',
    },
    footwear: DISPENSARY_THEME,
    peptides: {
        colors: {
            canopy: '#071b17',
            canopy2: '#05120f',
            canopy3: '#19382f',
            amber: '#4cdca5',
            amberLight: '#9ee8ce',
            amberDim: '#197052',
            sage: '#b9cec7',
            sageDim: '#78968c',
            paper: '#f4f7f6',
            paper2: '#dff3eb',
            ink: '#10231e',
            inkSoft: '#526a62',
        },
        radius: '0.375rem',
        fonts: { display: 'peptideDisplay', body: 'spaceGrotesk', mono: 'ibmPlexMono' },
        productCardVariant: 'clinical',
    },
}

export function storefrontTheme(kind: string): StorefrontTheme {
    return STOREFRONT_THEMES[kind as StorefrontKind] ?? STOREFRONT_THEMES.general
}
