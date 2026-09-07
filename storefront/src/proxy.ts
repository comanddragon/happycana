import { NextRequest, NextResponse } from 'next/server'
import { DEFAULT_STOREFRONT_SLUG, isLocalDevelopmentHost } from '@/lib/storefront'

const LAN_STOREFRONT_COOKIE = 'axiom-storefront'

function validStorefrontSlug(value: string | null | undefined): value is string {
    return Boolean(value && /^[a-z0-9][a-z0-9-]{0,62}$/.test(value))
}

export function proxy(request: NextRequest) {
    const headers = new Headers(request.headers)
    const publicHost = request.headers.get('x-forwarded-host')?.split(',', 1)[0]?.trim()
        || request.headers.get('host')
    const requestedSlug = request.nextUrl.searchParams.get('storefront')?.toLowerCase()
    const savedSlug = request.cookies.get(LAN_STOREFRONT_COOKIE)?.value.toLowerCase()
    const localSlug = validStorefrontSlug(requestedSlug)
        ? requestedSlug
        : validStorefrontSlug(savedSlug)
            ? savedSlug
            : DEFAULT_STOREFRONT_SLUG

    if (publicHost && isLocalDevelopmentHost(publicHost) && localSlug) {
        headers.set('x-storefront', localSlug)
        headers.delete('x-storefront-host')
    } else if (publicHost) {
        headers.set('x-storefront-host', publicHost)
    }
    const response = NextResponse.next({ request: { headers } })
    if (publicHost && isLocalDevelopmentHost(publicHost) && validStorefrontSlug(requestedSlug)) {
        response.cookies.set(LAN_STOREFRONT_COOKIE, requestedSlug, {
            httpOnly: true,
            sameSite: 'lax',
            path: '/',
            maxAge: 60 * 60 * 24 * 30,
        })
    }
    return response
}

export const config = {
    matcher: ['/((?!_next/static|_next/image|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)'],
}
