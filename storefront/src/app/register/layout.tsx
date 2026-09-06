// app/register/layout.tsx
// Same reasoning as app/login/layout.tsx: page.tsx is a client component,
// so metadata is attached via this server-component layout instead.
import type { Metadata } from 'next'
import React from "react";

export const metadata: Metadata = {
    title: 'Create Account',
    robots: { index: false, follow: false },
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
    return children
}
