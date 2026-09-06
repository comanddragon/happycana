// lib/queryKeys.ts
// Central react-query key factory. Kept dependency-free (no axios, zustand,
// or hooks) so it's safe to import from Server Components — e.g. to
// prefetch a query server-side under the exact same key a client
// component's useQuery(...) will look for during hydration.

export const qk = {
    products:      (params?: object) => ['products', params],
    product:       (slug: string)    => ['product', slug],
    categories:    ()                => ['categories'],
    category:      (slug: string)    => ['category', slug],
    brands:        ()                => ['brands'],
    brand:         (slug: string)    => ['brand', slug],
    effects:       ()                => ['effects'],
    cart:          ()                => ['cart'],
    orders:        (params?: object) => ['orders', params],
    order:         (id: string)      => ['order', id],
    notifications: ()                => ['notifications'],
    me:            ()                => ['me'],
    addresses:     ()                => ['addresses'],
    shipping:      ()                => ['shipping-methods'],
    paymentMethods: ()               => ['payment-methods'],
} as const
