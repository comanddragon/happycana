import { useEffect, type RefObject } from 'react'

export function useClickOutside<T extends HTMLElement>(
    ref: RefObject<T | null>,
    handler: () => void,
) {
    useEffect(() => {
        function onPointerDown(e: PointerEvent) {
            const el = ref.current
            if (!el || el.contains(e.target as Node)) return
            handler()
        }
        document.addEventListener('pointerdown', onPointerDown)
        return () => document.removeEventListener('pointerdown', onPointerDown)
    }, [ref, handler])
}
