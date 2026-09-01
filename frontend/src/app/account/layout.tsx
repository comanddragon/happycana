// app/account/layout.tsx
import type { Metadata } from 'next'
import { AccountShell } from '@/components/account/AccountShell'

// Account pages are private, user-specific, and have no unique content to
// rank — the interactive nav lives in AccountShell (a client component)
// since metadata exports aren't allowed there.
export const metadata: Metadata = {
    robots: { index: false, follow: false },
}

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return <AccountShell>{children}</AccountShell>
}
