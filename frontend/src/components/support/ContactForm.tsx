'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const SUPPORT_EMAIL = 'support@happycana.com'

export function ContactForm() {
    const [name, setName]     = useState('')
    const [email, setEmail]   = useState('')
    const [subject, setSubject] = useState('')
    const [message, setMessage] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        const body = `${message}\n\n— ${name} (${email})`
        window.location.href =
            `mailto:${SUPPORT_EMAIL}?subject=${encodeURIComponent(subject || 'Question from happycana.com')}&body=${encodeURIComponent(body)}`
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2">
                <div className="space-y-1.5">
                    <Label htmlFor="name">Name</Label>
                    <Input className="bg-white" id="name" required value={name} onChange={e => setName(e.target.value)} />
                </div>
                <div className="space-y-1.5">
                    <Label htmlFor="email">Email</Label>
                    <Input className="bg-white" id="email" type="email" required value={email} onChange={e => setEmail(e.target.value)} />
                </div>
            </div>
            <div className="space-y-1.5">
                <Label htmlFor="subject">Subject</Label>
                <Input className="bg-white" id="subject" required value={subject} onChange={e => setSubject(e.target.value)} />
            </div>
            <div className="space-y-1.5">
                <Label htmlFor="message">Message</Label>
                <textarea
                    id="message"
                    required
                    rows={5}
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    className={cn(
                        "bg-white w-full min-w-0 rounded-md border border-input px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none",
                        "focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50",
                        "placeholder:text-muted-foreground md:text-sm",
                    )}
                />
            </div>
            <Button type="submit" className="rounded-full">Send message</Button>
            <p className="text-xs text-hc-ink-soft">
                Opens your email client addressed to {SUPPORT_EMAIL}. Prefer live help? Use the chat widget in the corner instead.
            </p>
        </form>
    )
}
