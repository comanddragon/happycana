import { act, cleanup, renderHook } from '@testing-library/react'
import Cookies from 'js-cookie'
import { toast } from 'sonner'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useChatRoomWS } from '../useChat'

vi.mock('js-cookie', () => ({
    default: { get: vi.fn() },
}))

vi.mock('sonner', () => ({
    toast: { error: vi.fn(), success: vi.fn() },
}))

vi.mock('../useWebSocket', () => ({
    getWsBase: () => 'ws://example.test/ws',
}))

class MockWebSocket {
    static readonly CONNECTING = 0
    static readonly OPEN = 1
    static readonly CLOSING = 2
    static readonly CLOSED = 3
    static instances: MockWebSocket[] = []

    readonly url: string
    readyState = MockWebSocket.CONNECTING
    onopen: ((event: Event) => void) | null = null
    onmessage: ((event: MessageEvent) => void) | null = null
    onclose: ((event: CloseEvent) => void) | null = null
    onerror: ((event: Event) => void) | null = null
    send = vi.fn()

    constructor(url: string | URL) {
        this.url = String(url)
        MockWebSocket.instances.push(this)
    }

    close() {
        this.readyState = MockWebSocket.CLOSED
    }

    closeWith(code: number) {
        this.readyState = MockWebSocket.CLOSED
        this.onclose?.(new CloseEvent('close', { code }))
    }
}

describe('useChatRoomWS reconnect handling', () => {
    beforeEach(() => {
        vi.useFakeTimers()
        vi.stubGlobal('WebSocket', MockWebSocket)
        MockWebSocket.instances = []
        vi.mocked(Cookies.get as (name: string) => string | undefined).mockReturnValue('test-token')
    })

    afterEach(() => {
        cleanup()
        vi.clearAllTimers()
        vi.useRealTimers()
        vi.unstubAllGlobals()
        vi.clearAllMocks()
    })

    it.each([
        [4001, 'Chat session expired — refresh the page to reconnect.'],
        [4003, "You don't have access to this conversation."],
    ])('treats close code %i as terminal and surfaces an auth error', (code, message) => {
        const { result } = renderHook(() => useChatRoomWS('room-1'))

        act(() => vi.advanceTimersByTime(100))
        expect(MockWebSocket.instances).toHaveLength(1)
        expect(MockWebSocket.instances[0].url).toBe(
            'ws://example.test/ws/chat/room-1/?token=test-token',
        )

        act(() => MockWebSocket.instances[0].closeWith(code))

        expect(result.current.connected).toBe(false)
        expect(result.current.authError).toBe(true)
        expect(toast.error).toHaveBeenCalledWith(message)

        act(() => vi.advanceTimersByTime(60_000))
        expect(MockWebSocket.instances).toHaveLength(1)
    })

    it('retries normal drops with exponential backoff and stops after five retries', () => {
        const { result } = renderHook(() => useChatRoomWS('room-1'))

        act(() => vi.advanceTimersByTime(100))
        expect(MockWebSocket.instances).toHaveLength(1)

        const retryDelays = [2_000, 4_000, 8_000, 16_000, 30_000]
        retryDelays.forEach((delay, retryIndex) => {
            act(() => MockWebSocket.instances[retryIndex].closeWith(1006))

            act(() => vi.advanceTimersByTime(delay - 1))
            expect(MockWebSocket.instances).toHaveLength(retryIndex + 1)

            act(() => vi.advanceTimersByTime(1))
            expect(MockWebSocket.instances).toHaveLength(retryIndex + 2)
        })

        act(() => MockWebSocket.instances[5].closeWith(1006))
        act(() => vi.advanceTimersByTime(60_000))

        expect(MockWebSocket.instances).toHaveLength(6)
        expect(result.current.authError).toBe(false)
        expect(toast.error).not.toHaveBeenCalled()
    })
})
