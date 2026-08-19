import { useSyncExternalStore } from 'react'

function subscribe() {
    return () => {}
}

/** True once hydrated on the client, false during SSR and the first client
 *  render — same guarantee as the setMounted(true)-in-an-effect pattern,
 *  without a dedicated effect+render cycle to produce it. */
export function useMounted(): boolean {
    return useSyncExternalStore(
        subscribe,
        () => true,   // client snapshot
        () => false,  // server snapshot
    )
}
