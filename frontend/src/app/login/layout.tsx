// app/login/layout.tsx
import type { Metadata } from 'next'

// Auth pages have no unique content to rank and shouldn't be indexed —
// the page itself is a client component so metadata can't live there.
export const metadata: Metadata = {
    robots: { index: false, follow: false },
}

export default function LoginLayout({ children }: { children: React.ReactNode }) {
    return children
}
