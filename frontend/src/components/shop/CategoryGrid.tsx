import Link from 'next/link'
import Image from 'next/image'
import { mediaUrl } from '@/lib/utils'
import type { Category } from '@/types'

function CategoryTile({ cat }: { cat: Category }) {
    return (
        <Link
            href={`/shop/products?category=${cat.slug}`}
            className="group relative flex aspect-square flex-col items-center justify-end overflow-hidden rounded-2xl bg-white px-4 py-5 text-center transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hc-amber focus-visible:ring-offset-2"
        >
            {cat.image_url && (
                // <Image
                //     src={mediaUrl(cat.image_url)!}
                //     alt=""
                //     fill
                //     quality={65}
                //     sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 200px"
                //     className="object-cover transition-transform duration-300 group-hover:scale-105"
                // />
                <img
                    src={mediaUrl(cat.image_url)!}
                    alt={cat.name}
                    className="absolute inset-0 h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />

            )}
            <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />
            <div className="relative">
                <p className="font-hc-display text-base font-medium text-white">{cat.name}</p>
                {cat.children && cat.children.length > 0 && (
                    <p className="mt-1 font-hc-mono text-[10.5px] tracking-wide text-white/75">
                        {cat.children.length} SUBCATEGORIES
                    </p>
                )}
            </div>
        </Link>
    )
}

export function CategoryGridSkeleton() {
    return (
        <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="aspect-square animate-pulse rounded-2xl bg-hc-paper-2" />
            ))}
        </div>
    )
}

export function CategoryGrid({ categories }: { categories: Category[] }) {
    const rest = categories.slice(8, 11)

    return (
        <>
            <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
                {categories.slice(0, 8).map(cat => (
                    <CategoryTile key={cat.id} cat={cat} />
                ))}
            </div>
            {rest.length > 0 && (
                <div className="mt-3.5 flex flex-wrap justify-center gap-3.5">
                    {rest.map(cat => (
                        <div key={cat.id} className="w-[calc(50%-7px)] sm:w-[calc(25%-10.5px)]">
                            <CategoryTile cat={cat} />
                        </div>
                    ))}
                </div>
            )}
        </>
    )
}