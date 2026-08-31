type LoaderProps = {
    src: string
    width: number
    quality?: number
}

export default function imgixLoader({
                                        src,
                                        width,
                                        quality,
                                    }: LoaderProps): string {

    // Local/static assets (e.g. from /public, or dev-proxied backend media
    // that mediaUrl() has shortened to a bare path) aren't imgix-hosted, so
    // there's nothing to resize server-side. Append a width param anyway so
    // Next's "does this loader implement width" probe sees the output change
    // between calls and doesn't warn — the browser will just ignore it.
    if (src.startsWith('/')) {
        const separator = src.includes('?') ? '&' : '?'
        return `${src}${separator}w=${width}`
    }

    let url: URL

    try {
        url = new URL(src)
    } catch {
        return src
    }

    // Dev-only: backend media served through localhost isn't imgix-hosted
    // either, so treat it the same as a local path above.
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') {
        url.searchParams.set('w', String(width))
        return url.toString()
    }

    // Imgix-hosted images.
    if (url.hostname.endsWith('imgix.dispenseapp.com')) {
        url.searchParams.set('w', String(width))
        url.searchParams.set('q', String(quality ?? 65))
        url.searchParams.set('auto', 'format,compress')
        url.searchParams.set('fit', 'max')

        return url.toString()
    }

    return src
}