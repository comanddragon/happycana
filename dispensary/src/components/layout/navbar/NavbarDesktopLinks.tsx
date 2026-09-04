import Link from 'next/link'
import { cn } from '@/lib/utils'
import { NAV_LINKS } from './constants'
import { NavCategoriesMenu } from '@/components/layout/navbar/NavCategoriesMenu'

export function NavbarDesktopLinks({ pathname }: { pathname: string }) {
    // Pick the single most specific (longest) matching href instead of
    // highlighting every link whose href is a prefix of the current path.
    // e.g. on /shop/products/some-slug, only "Products" should light up,
    // not "Shop" too.
    const matchingHrefs = NAV_LINKS
        .map((item) => item.href?.split('?')[0].split('#')[0])
        .filter((href): href is string => !!href && href.startsWith('/shop') && pathname.startsWith(href))

    const bestMatch = matchingHrefs.sort((a, b) => b.length - a.length)[0]

    return (
        <nav className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((item) => {
                const itemHref = item.href?.split('?')[0].split('#')[0]
                const isActive = !!itemHref && itemHref === bestMatch

                if (item.dynamic) {
                    return <NavCategoriesMenu key={item.label} />
                }

                return (
                    <Link
                        key={item.label}
                        href={item.href ?? '#'}
                        className={cn(
                            'text-sm font-medium text-hc-sage transition-colors hover:text-hc-paper',
                            isActive && 'text-hc-paper'
                        )}
                    >
                        {item.label}
                    </Link>
                )
            })}
        </nav>
    )
}