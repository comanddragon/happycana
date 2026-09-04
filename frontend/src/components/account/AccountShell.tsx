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

