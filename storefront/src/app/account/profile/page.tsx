'use client'

import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useMe, qk } from '@/hooks/useApi'
import { userService } from '@/lib/services'
import { extractErrorMessage } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

const schema = z.object({
    first_name: z.string().min(1, 'Required'),
    last_name:  z.string().min(1, 'Required'),
    phone:      z.string().optional(),
})
type FormData = z.infer<typeof schema>

export default function ProfilePage() {
    const { data: user, isLoading } = useMe()
    const qc = useQueryClient()

    const { register, handleSubmit, reset, formState: { errors, isDirty } } = useForm<FormData>({
        resolver: zodResolver(schema),
    })

    useEffect(() => {
        if (user) reset({ first_name: user.first_name, last_name: user.last_name, phone: user.phone })
    }, [user, reset])

    const update = useMutation({
        mutationFn: (data: FormData) => userService.update(data),
        onSuccess: () => { qc.invalidateQueries({ queryKey: qk.me() }); toast.success('Profile updated') },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })

    if (isLoading) return (
        <div className="space-y-4">
            <Skeleton className="h-8 w-1/3" />
            <Card><CardContent className="p-6 space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
            </CardContent></Card>
        </div>
    )

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-display font-semibold">Profile</h1>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-4">
                        <Avatar className="h-16 w-16">
                            <AvatarFallback className="bg-gradient-to-br from-brand-400 to-brand-700 text-white text-2xl">
                                {user?.first_name?.[0] ?? user?.email?.[0]?.toUpperCase() ?? 'U'}
                            </AvatarFallback>
                        </Avatar>
                        <div>
                            <CardTitle>{user?.first_name} {user?.last_name}</CardTitle>
                            <p className="text-sm text-muted-foreground">{user?.email}</p>
                        </div>
                    </div>
                </CardHeader>
                <Separator />
                <CardContent className="pt-6">
                    <form onSubmit={handleSubmit(d => update.mutate(d))} className="space-y-4">
                        <div className="grid sm:grid-cols-2 gap-4">
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
                            <Label>Email</Label>
                            <Input value={user?.email ?? ''} disabled />
                            <p className="text-xs text-muted-foreground">Email cannot be changed.</p>
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="phone">Phone</Label>
                            <Input id="phone" {...register('phone')} placeholder="+1 (555) 000-0000" />
                        </div>

                        <div className="flex justify-end pt-2">
                            <Button type="submit" disabled={update.isPending || !isDirty}>
                                {update.isPending ? 'Saving…' : 'Save Changes'}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}