// app/account/AccountLayoutClient.tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { User, Package, Mail, MapPin, Shield, ChevronRight } from 'lucide-react'
import { CartDrawer } from '@/components/shop/CartDrawer'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { href: '/account/profile',   icon: User,     label: 'Profile' },
    { href: '/account/chat',  icon: Mail,   label: 'Chat' },
  { href: '/account/orders',    icon: Package,  label: 'Orders' },
  { href: '/account/addresses', icon: MapPin,   label: 'Addresses' },
  { href: '/account/security',  icon: Shield,   label: 'Security' },

]

export default function AccountLayoutClient({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex flex-col">
      <CartDrawer />
      <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <aside className="lg:col-span-1">
            <nav className="card overflow-hidden">
              <div className="p-4 border-b border-surface-100">
                <p className="text-xs font-semibold text-surface-500 uppercase tracking-widest">Account</p>
              </div>
              <div className="p-2">
                {NAV_ITEMS.map(({ href, icon: Icon, label }) => (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      'flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-colors',
                      pathname.startsWith(href)
                        ? 'bg-brand-50 text-brand-700'
                        : 'text-surface-700 hover:bg-surface-100'
                    )}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="h-4 w-4" />
                      {label}
                    </div>
                    {pathname.startsWith(href) && (
                      <ChevronRight className="h-3.5 w-3.5 text-brand-500" />
                    )}
                  </Link>
                ))}
              </div>
            </nav>
          </aside>

          {/* Content */}
          <div className="lg:col-span-3 animate-fade-in">{children}</div>
        </div>
      </main>
    </div>
  )
}
