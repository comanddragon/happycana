// lib/blog.ts
// Single source of truth for /blog posts: title, slug, dek, author, and
// timestamps. Mirrors the shape of lib/guides.ts (which powers /learn) —
// consumed by the /blog index, the sitemap, and each post's own metadata
// so nothing has to be kept in sync by hand across multiple files.

export interface BlogAuthor {
    name: string
    role: string
    bio: string
}

export const AUTHORS: Record<string, BlogAuthor> = {
    jana: {
        name: 'Jana Novakova',
        role: 'Staff Writer',
        bio: 'Jana covers the practical side of cannabis retail for HappyCana \u2014 gear, storage, and the small habits that make each session better.',
    },
}

export interface BlogPost {
    slug: string
    title: string
    /** One-line summary shown on cards and used as the meta description. */
    description: string
    /** Section tag shown as a pill above the title, e.g. "Guide", "Lifestyle". */
    tags: string[]
    author: keyof typeof AUTHORS
    publishedAt: string // ISO date
    readTime: string // e.g. "7 min"
}

export const BLOG_POSTS: BlogPost[] = [
    {
        slug: 'cannabis-accessories-5-essentials',
        title: 'Cannabis Accessories: The 5 Essentials Worth Owning',
        description:
            'Most of an accessory shop is gadgets you\u2019ll use once. Here\u2019s the short list that actually earns its shelf space \u2014 what to buy, what to skip, and how to keep it clean.',
        tags: ['Guide', 'Lifestyle'],
        author: 'jana',
        publishedAt: '2026-06-10',
        readTime: '7 min',
    },
    {
        slug: 'joint-filter-comparison-carbon-vs-paper',
        title: 'Joint Filter Comparison: Activated Carbon vs. Paper',
        description:
            'Crutches, carbon tips, and pre-made filters all do the same basic job differently. Here\u2019s how draw, filtration, and cost actually compare.',
        tags: ['Guide'],
        author: 'jana',
        publishedAt: '2026-05-28',
        readTime: '5 min',
    },
    {
        slug: 'joint-rolling-for-beginners',
        title: 'Joint Rolling for Beginners: Step-by-Step Guide',
        description:
            'Grind, funnel, roll, twist. A slower walkthrough of the four steps that make the difference between an even burn and a canoe.',
        tags: ['Guide', 'Getting Started'],
        author: 'jana',
        publishedAt: '2026-05-14',
        readTime: '6 min',
    },
]

export function getPost(slug: string): BlogPost | undefined {
    return BLOG_POSTS.find(p => p.slug === slug)
}

export function formatPostDate(iso: string): string {
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
