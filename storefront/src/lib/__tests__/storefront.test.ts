import { afterEach, describe, expect, it, vi } from 'vitest'

import { headers as requestHeaders } from 'next/headers'
import { isLocalDevelopmentHost, safeJsonLd } from '@/lib/storefront'
import { timedFetch } from '@/lib/timedFetch.server'
import { storefrontTheme } from '@/storefront/theme'

vi.mock('next/headers', () => ({
    headers: vi.fn(async () => new Headers({ host: 'peptides.example.com' })),
}))

describe('storefront request and SEO helpers', () => {
    afterEach(() => {
        vi.restoreAllMocks()
        vi.mocked(requestHeaders).mockResolvedValue(new Headers({ host: 'peptides.example.com' }))
    })

    it('forwards the public hostname to server requests', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{}'))

        await timedFetch('https://api.example/catalog/products/', {
            headers: { Accept: 'application/json' },
        })

        const headers = new Headers(fetchMock.mock.calls[0][1]?.headers)
        expect(headers.get('X-Storefront-Host')).toBe('peptides.example.com')
        expect(headers.get('Accept')).toBe('application/json')
    })

    it('keeps the explicit storefront selector for private LAN hosts', async () => {
        vi.mocked(requestHeaders).mockResolvedValue(new Headers({
            host: '192.168.1.182:3000',
            'x-storefront': 'peptides',
        }))
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{}'))

        await timedFetch('https://api.example/storefront/')

        const headers = new Headers(fetchMock.mock.calls[0][1]?.headers)
        expect(headers.get('X-Storefront')).toBe('peptides')
        expect(headers.get('X-Storefront-Host')).toBeNull()
    })

    it.each(['192.168.1.182:3000', '10.0.0.8:3000', '172.20.10.4:3000', '[::1]:3000'])(
        'recognizes %s as a local development host',
        host => expect(isLocalDevelopmentHost(host)).toBe(true),
    )

    it('escapes script-opening characters in structured data', () => {
        const encoded = safeJsonLd({ name: '</script><script>alert(1)</script>' })

        expect(encoded).not.toContain('<')
        expect(JSON.parse(encoded).name).toBe('</script><script>alert(1)</script>')
    })

    it('gives the hash storefront its own visual theme', () => {
        expect(storefrontTheme('hash')).not.toBe(storefrontTheme('dispensary'))
        expect(storefrontTheme('hash').colors.canopy).toBe('#1b1510')
    })
})
