// lib/guides.ts
// Single source of truth for the /learn answer-content pages: title,
// slug, and one-line description. Consumed by the /learn index, the
// sitemap, and the footer's "Learn" column so every surface that links to
// guides (and the sitemap that tells crawlers about them) stays in sync
// with the same list — add a guide here once and it shows up everywhere.

export interface Guide {
    slug: string
    title: string
    description: string
    /** Short label shown above the title, matches the site's "eyebrow" convention. */
    kicker: string
}

export const GUIDES: Guide[] = [
    {
        slug: 'indica-vs-sativa-vs-hybrid',
        title: 'Indica vs. Sativa vs. Hybrid: What Actually Differs',
        description: 'What the indica/sativa/hybrid labels really tell you, and what they don\u2019t.',
        kicker: 'BASICS',
    },
    {
        slug: 'how-long-do-edibles-take-to-kick-in',
        title: 'How Long Do Edibles Take to Kick In?',
        description: 'Onset time, why it varies so much, and why more isn\u2019t "not working yet."',
        kicker: 'EDIBLES',
    },
    {
        slug: 'what-is-a-cannabis-coa',
        title: 'What\u2019s on a Cannabis COA and Why It Matters',
        description: 'How to actually read a certificate of analysis before you trust a batch.',
        kicker: 'LAB TESTING',
    },
    {
        slug: 'terpenes-101',
        title: 'Terpenes 101: The Aromas Behind the Effects',
        description: 'What terpenes are, the common ones, and how they shape a strain\u2019s effects.',
        kicker: 'BASICS',
    },
    {
        slug: 'beginners-guide-to-cannabis-dosing',
        title: 'A Beginner\u2019s Guide to Cannabis Dosing',
        description: 'Why "start low, go slow" exists, and how to apply it across product types.',
        kicker: 'GETTING STARTED',
    },
]

export function getGuide(slug: string): Guide | undefined {
    return GUIDES.find(g => g.slug === slug)
}

// Maps a product's own attributes (compliance_category, cannabis_type,
// whether it has real lab data) to the single most relevant /learn guide,
// so product detail pages can link to real educational content instead of
// only the generic FAQ. Falls back to the beginner's dosing guide when
// nothing more specific applies.
export function getGuideForProduct(product: {
    compliance_category?: string
    cannabis_type?: string
    variants?: { lab?: unknown }[]
}): Guide {
    if (product.compliance_category === 'edibles') {
        return getGuide('how-long-do-edibles-take-to-kick-in')!
    }

    const cannabisType = product.cannabis_type
    if (cannabisType && cannabisType !== 'na') {
        return getGuide('indica-vs-sativa-vs-hybrid')!
    }

    const hasLab = product.variants?.some(v => v.lab)
    if (hasLab) {
        return getGuide('what-is-a-cannabis-coa')!
    }

    return getGuide('beginners-guide-to-cannabis-dosing')!
}
