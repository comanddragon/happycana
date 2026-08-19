// app/(shop)/layout.tsx
import React from "react";
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: 'HappyCana — Shop the Menu',
    template: '%s | HappyCana',
  },
  description: 'Shop Flower, edibles, and concentrates from small-batch growers, third-party tested and delivered same-day.',
}

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="font-hc-body bg-hc-paper min-h-screen flex flex-col">
      <main className="flex-1">{children}</main>
    </div>
  )
}
