// app/account/layout.tsx
// Server component so it can export `metadata` (noindex — every /account/*
// page is a signed-in user's private data with no unique public content).
// All the interactive nav/UI lives in AccountLayoutClient.
import type { Metadata } from 'next'
import AccountLayoutClient from './AccountLayoutClient'
import React from "react";

export const metadata: Metadata = {
    robots: { index: false, follow: false },
}

export default function AccountLayout({ children }: { children: React.ReactNode }) {
    return <AccountLayoutClient>{children}</AccountLayoutClient>
}
