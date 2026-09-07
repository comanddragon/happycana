import Link from 'next/link'
import Image from 'next/image'
import { mediaUrl } from '@/lib/utils'
import type { Category } from '@/types'

// Category uploads are optional. Use real catalogue photography from the
// existing Imgix CDN as a storefront fallback instead of showing an empty
// gradient when a category has no image in the CMS yet.
const CATEGORY_CDN_IMAGES: Record<string, string> = {
    accessories: 'https://imgix.dispenseapp.com/145c714690909516_1743981167275-681704378-86768548.png',
    beverages: 'https://imgix.dispenseapp.com/145c714690909516_1778180667077-195172706-shhfshgsg.webp',
    'cbd-products': 'https://imgix.dispenseapp.com/145c714690909516_1768928274214-858001206-Vape_Specs.png',
    concentrates: 'https://imgix.dispenseapp.com/145c714690909516_1777388397629-785352325-4352345.jpg',
    edibles: 'https://imgix.dispenseapp.com/145c714690909516_1779201340005-919424689-35345345.avif',
    flower: 'https://imgix.dispenseapp.com/145c714690909516_1781719195742-35570527-54325234.png',
    'pre-rolls': 'https://imgix.dispenseapp.com/145c714690909516_1742468117692-457039296-899808908908.png',
    tinctures: 'https://imgix.dispenseapp.com/145c714690909516_1749723350648-817544208-5416516519818525252.jpg',
    topicals: 'https://imgix.dispenseapp.com/145c714690909516_1749723176656-191914202-452141748485424.jpg',
    vaporizers: 'https://imgix.dispenseapp.com/145c714690909516_1703343990098-451147540-gorilla_glu_vape.webp',
}

function slugSeed(slug: string) {
    return Array.from(slug).reduce((total, character) => total + character.charCodeAt(0), 0)
}

function PeptideCategoryArtwork({ slug }: { slug: string }) {
    const seed = slugSeed(slug)
    const shift = seed % 42

    return (
        <div className="absolute inset-0 overflow-hidden bg-[#071b17]" aria-hidden="true">
            <div className="absolute inset-0 opacity-30 [background-image:linear-gradient(rgba(76,220,165,.16)_1px,transparent_1px),linear-gradient(90deg,rgba(76,220,165,.16)_1px,transparent_1px)] [background-size:24px_24px]" />
            <div
                className="absolute h-36 w-36 rounded-full border border-[#9ee8ce]/40 bg-[#4cdca5]/10 shadow-[0_0_55px_rgba(76,220,165,.24)]"
                style={{ left: `${8 + shift / 2}%`, top: `${8 + shift / 3}%` }}
            />
            <svg viewBox="0 0 200 200" className="absolute inset-0 h-full w-full text-[#9ee8ce] opacity-90">
                <path d={`M25 ${62 + shift / 3} L72 42 L111 ${76 + shift / 5} L164 45 M72 42 L84 128 L144 151 M111 ${76 + shift / 5} L84 128 L166 113`} fill="none" stroke="currentColor" strokeWidth="1.5" opacity=".48" />
                {[[25, 62 + shift / 3], [72, 42], [111, 76 + shift / 5], [164, 45], [84, 128], [144, 151], [166, 113]].map(([x, y], index) => (
                    <g key={index}>
                        <circle cx={x} cy={y} r={index % 3 === 0 ? 10 : 6} fill="#071b17" stroke="currentColor" strokeWidth="2" />
                        <circle cx={x} cy={y} r="2" fill="currentColor" />
                    </g>
                ))}
            </svg>
            <div className="absolute right-4 top-4 font-hc-mono text-[9px] tracking-[0.24em] text-[#9ee8ce]/65">SEQ {String(seed % 99).padStart(2, '0')}</div>
        </div>
    )
}

function HashCategoryArtwork({ slug }: { slug: string }) {
    const seed = slugSeed(slug)
    const rotation = (seed % 22) - 11
    const offset = seed % 24

    return (
        <div className="absolute inset-0 overflow-hidden bg-[#1b1510]" aria-hidden="true">
            <div className="absolute inset-0 opacity-35 [background-image:radial-gradient(circle_at_center,rgba(243,200,110,.26)_0,rgba(243,200,110,.08)_28%,transparent_68%)]" />
            <div className="absolute -left-8 -top-8 h-32 w-32 rounded-full border border-[#d9962f]/20" />
            <div
                className="absolute aspect-square w-[58%] rounded-[42%] border border-[#f3c86e]/45 bg-[radial-gradient(circle_at_35%_30%,#d79b43_0%,#916025_27%,#4a2e16_66%,#24150b_100%)] shadow-[0_18px_35px_rgba(0,0,0,.5),inset_0_0_22px_rgba(243,200,110,.3)]"
                style={{ right: `${5 + offset / 3}%`, top: `${9 + offset / 4}%`, transform: `rotate(${rotation}deg)` }}
            >
                <div className="absolute inset-[13%] rounded-[40%] border border-dashed border-[#f3c86e]/30" />
                <div className="absolute left-[27%] top-[21%] h-1.5 w-1.5 rounded-full bg-[#f3c86e]/55" />
                <div className="absolute bottom-[28%] right-[22%] h-1 w-1 rounded-full bg-[#f3c86e]/65" />
            </div>
            <div className="absolute left-4 top-4 font-hc-mono text-[9px] tracking-[0.24em] text-[#f3c86e]/65">BATCH {String(seed % 99).padStart(2, '0')}</div>
        </div>
    )
}

function CategoryArtwork({ slug }: { slug: string }) {
    if (slug.startsWith('peptide-')) return <PeptideCategoryArtwork slug={slug} />
    if (slug.startsWith('hash-')) return <HashCategoryArtwork slug={slug} />
    return null
}

function CategoryTile({ cat }: { cat: Category }) {
    const imageUrl = mediaUrl(cat.image_url || CATEGORY_CDN_IMAGES[cat.slug])

    return (
        <Link
            href={`/shop/categories/${cat.slug}`}
            className="group relative flex aspect-square flex-col items-center justify-end overflow-hidden rounded-2xl bg-white px-4 py-5 text-center transition-all duration-200 hover:-translate-y-1 hover:border-hc-amber hover:shadow-[0_16px_30px_-14px_rgba(23,20,15,0.25)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hc-amber focus-visible:ring-offset-2"
        >
            {imageUrl ? (
                <Image
                    src={imageUrl}
                    alt={cat.name}
                    fill
                    quality={65}
                    sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 200px"
                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                />
            ) : (
                <CategoryArtwork slug={cat.slug} />
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
