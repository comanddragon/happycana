'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { userService } from '@/lib/services'
import { extractErrorMessage } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

const schema = z.object({
    old_password:     z.string().min(1, 'Required'),
    new_password:     z.string().min(8, 'Min 8 characters'),
    confirm_password: z.string(),
}).refine(d => d.new_password === d.confirm_password, {
    message: 'Passwords must match', path: ['confirm_password'],
})
type FormData = z.infer<typeof schema>

export default function SecurityPage() {
    const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
        resolver: zodResolver(schema),
    })

    const change = useMutation({
        mutationFn: ({ old_password, new_password }: { old_password: string; new_password: string }) =>
            userService.changePassword(old_password, new_password),
        onSuccess: () => { toast.success('Password changed successfully'); reset() },
        onError: (e) => toast.error(extractErrorMessage(e)),
    })

    const fields = [
        { name: 'old_password',     label: 'Current password',      autoComplete: 'current-password' },
        { name: 'new_password',     label: 'New password',          autoComplete: 'new-password' },
        { name: 'confirm_password', label: 'Confirm new password',  autoComplete: 'new-password' },
    ] as const

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-display font-semibold">Security</h1>

            <Card className="max-w-md">
                <CardHeader>
                    <CardTitle>Change Password</CardTitle>
                    <CardDescription>Choose a strong password you haven&apos;t used before.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(d => change.mutate(d))} className="space-y-4">
                        {fields.map(({ name, label, autoComplete }) => (
                            <div key={name} className="space-y-1.5">
                                <Label htmlFor={name}>{label}</Label>
                                <Input id={name} {...register(name)} type="password" autoComplete={autoComplete} placeholder="••••••••" />
                                {errors[name] && <p className="text-xs text-destructive">{errors[name]?.message}</p>}
                            </div>
                        ))}
                        <Button type="submit" disabled={change.isPending} className="mt-2">
                            {change.isPending ? 'Updating…' : 'Update Password'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}