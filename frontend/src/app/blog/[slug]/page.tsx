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
    }
}

export default async function Page({ params }: PageProps) {
    const { slug } = await params
    const post = await getBlogPost(slug)
    if (!post) notFound()

    return <BlogArticle post={post} />
}
