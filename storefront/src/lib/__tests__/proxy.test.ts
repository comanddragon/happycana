import { describe, expect, it } from 'vitest'
import { NextRequest } from 'next/server'

import { proxy } from '@/proxy'

describe('LAN storefront selection', () => {
    it('selects and remembers a storefront from the raw LAN IP URL', () => {
        const request = new NextRequest('http://192.168.1.182:3000/?storefront=hash', {
            headers: { host: '192.168.1.182:3000' },
        })
        const response = proxy(request)

        expect(response.headers.get('x-middleware-request-x-storefront')).toBe('hash')
        expect(response.cookies.get('axiom-storefront')?.value).toBe('hash')
    })

    it('uses the remembered storefront on following LAN requests', () => {
        const request = new NextRequest('http://192.168.1.182:3000/shop/products', {
            headers: { host: '192.168.1.182:3000', cookie: 'axiom-storefront=hash' },
        })
        const response = proxy(request)

        expect(response.headers.get('x-middleware-request-x-storefront')).toBe('hash')
    })

    it('does not accept malformed storefront selectors', () => {
        const request = new NextRequest('http://192.168.1.182:3000/?storefront=../../admin', {
            headers: { host: '192.168.1.182:3000' },
        })
        const response = proxy(request)

        expect(response.cookies.get('axiom-storefront')).toBeUndefined()
    })
})
