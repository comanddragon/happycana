// app/blog/[slug]/page.tsx
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { BlogArticle } from '@/components/blog/BlogArticle'
import { getBlogPost } from '@/lib/blog.server'

interface PageProps {
    params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const { slug } = await params
    const post = await getBlogPost(slug)
    if (!post) return {}

    return {
        title: post.title,
        description: post.description,
        alternates: { canonical: `/blog/${post.slug}` },
        // Falls back to the root layout's generic OG/Twitter defaults
        // without this — every post has a real image and description
        // already, so shares should use them instead of the generic
        // site-wide card. See SEO & AEO audit.md.
        openGraph: {
            type: 'article',
            title: post.title,
            description: post.description,
            publishedTime: post.published_at ?? undefined,
            authors: post.author ? [post.author] : undefined,
            ...(post.image && { images: [{ url: post.image }] }),
        },
        twitter: {
            card: post.image ? 'summary_large_image' : 'summary',
            title: post.title,
            description: post.description,
            ...(post.image && { images: [post.image] }),
        },
    }
}

export default async function Page({ params }: PageProps) {
    const { slug } = await params
    const post = await getBlogPost(slug)
    if (!post) notFound()

    return <BlogArticle post={post} />
}
