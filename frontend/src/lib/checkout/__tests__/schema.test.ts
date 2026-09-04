import { describe, it, expect } from 'vitest'
import { addressSchema } from '../schema'

describe('addressSchema (checkout)', () => {
    const validAddress = {
        line1: '123 Main St',
        city: 'Yaoundé',
        state: 'Centre',
        postal_code: '00237',
        country: 'CM',
    }

    it('accepts a fully valid address', () => {
        const result = addressSchema.safeParse(validAddress)
        expect(result.success).toBe(true)
    })

    it('accepts an optional line2', () => {
        const result = addressSchema.safeParse({ ...validAddress, line2: 'Apt 4B' })
        expect(result.success).toBe(true)
    })

    it('rejects a line1 that is too short', () => {
        const result = addressSchema.safeParse({ ...validAddress, line1: 'ab' })
        expect(result.success).toBe(false)
    })

    it('rejects a missing city', () => {
        const { city: _city, ...rest } = validAddress
        const result = addressSchema.safeParse(rest)
        expect(result.success).toBe(false)
    })

    it('rejects a state that is too short', () => {
        const result = addressSchema.safeParse({ ...validAddress, state: 'C' })
        expect(result.success).toBe(false)
    })

    it('rejects a postal_code that is too short', () => {
        const result = addressSchema.safeParse({ ...validAddress, postal_code: '1' })
        expect(result.success).toBe(false)
    })

    it('rejects a country that is too short', () => {
        const result = addressSchema.safeParse({ ...validAddress, country: 'C' })
        expect(result.success).toBe(false)
    })
})
