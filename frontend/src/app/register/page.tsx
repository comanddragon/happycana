'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Loader2, ShoppingBag } from 'lucide-react'
import { authService } from '@/lib/services'
import { useAuthStore } from '@/store/auth'
import { extractErrorMessage } from '@/lib/api'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

const schema = z.object({
    first_name: z.string().min(1, 'Required'),
    last_name:  z.string().min(1, 'Required'),
    email:      z.string().email('Valid email required'),
    password:   z.string().min(8, 'Min 8 characters'),
    password2: z.string(),
}).refine(d => d.password === d.password2, {
    message: 'Passwords must match',
    path: ['confirm_password'],
})
type FormData = z.infer<typeof schema>

export default function RegisterPage() {
    const router  = useRouter()
    const setUser = useAuthStore(s => s.setUser)
    const [showPw, setShowPw]   = useState(false)
    const [loading, setLoading] = useState(false)

    const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
        resolver: zodResolver(schema),
    })

    const onSubmit = async (data: FormData) => {
        setLoading(true)
        try {
            const res = await authService.register(data)
            setUser(res.user)
            toast.success('Account created! Welcome to ShopForge.')
            router.push('/shop/products')
        } catch (e) {
            toast.error(extractErrorMessage(e))
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-muted/30 flex items-center justify-center p-4">
            <div className="w-full max-w-md space-y-6">
                <div className="text-center">
                    <Link href="/" className="inline-flex items-center gap-2 justify-center">
                        <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                            <ShoppingBag className="h-5 w-5 text-white" />
                        </div>
                        <span className="font-display text-2xl font-semibold">ShopForge</span>
                    </Link>
                </div>

                <Card>
                    <CardHeader className="text-center">
                        <CardTitle className="font-display text-2xl">Create an account</CardTitle>
                        <CardDescription>Join thousands of happy customers</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1.5">
                                    <Label htmlFor="first_name">First name</Label>
                                    <Input id="first_name" {...register('first_name')} />
                                    {errors.first_name && <p className="text-xs text-destructive">{errors.first_name.message}</p>}
                                </div>
                                <div className="space-y-1.5">
                                    <Label htmlFor="last_name">Last name</Label>
                                    <Input id="last_name" {...register('last_name')} />
                                    {errors.last_name && <p className="text-xs text-destructive">{errors.last_name.message}</p>}
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="email">Email</Label>
                                <Input id="email" {...register('email')} type="email" autoComplete="email" placeholder="you@example.com" />
                                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="password">Password</Label>
                                <div className="relative">
                                    <Input id="password" {...register('password')} type={showPw ? 'text' : 'password'}
                                           placeholder="Min 8 characters" className="pr-10" />
                                    <Button type="button" variant="ghost" size="icon"
                                            className="absolute right-0 top-0 h-full px-3 text-muted-foreground"
                                            onClick={() => setShowPw(!showPw)}>
                                        {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    </Button>
                                </div>
                                {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="password2">Confirm password</Label>
                                <Input id="password2" {...register('password2')} type="password" placeholder="Repeat password" />
                                {errors.password2 && <p className="text-xs text-destructive">{errors.password2.message}</p>}
                            </div>

                            <Button type="submit" className="w-full" size="lg" disabled={loading}>
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create Account'}
                            </Button>
                        </form>
                    </CardContent>
                    <CardFooter className="justify-center">
                        <p className="text-sm text-muted-foreground">
                            Already have an account?{' '}
                            <Link href="/login" className="text-brand-600 font-medium hover:underline">Sign in</Link>
                        </p>
                    </CardFooter>
                </Card>
            </div>
        </div>
    )
}