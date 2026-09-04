// app/login/layout.tsx
// page.tsx here is a client component ('use client'), so it can't export
// `metadata` itself — a server-component layout alongside it is the
// standard way to attach page-level metadata (here: noindex, since a login
// form has no unique content worth surfacing in search results).
import type { Metadata } from 'next'
import React from "react";

export const metadata: Metadata = {
    title: 'Sign In',
    robots: { index: false, follow: false },
}

export default function LoginLayout({ children }: { children: React.ReactNode }) {
    return children
}
