import { z } from 'zod'

export const addressSchema = z.object({
    line1:       z.string().min(3, 'Required'),
    line2:       z.string().optional(),
    city:        z.string().min(2, 'Required'),
    state:       z.string().min(2, 'Required'),
    postal_code: z.string().min(3, 'Required'),
    country:     z.string().min(2, 'Required'),
})

export type AddressForm = z.infer<typeof addressSchema>
