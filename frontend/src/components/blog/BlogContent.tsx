'use client'

import { useEffect, useRef } from 'react'

interface Props {
    html: string
}

export function BlogContent({ html }: Props) {
    const rootRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const root = rootRef.current
        if (!root) return

        const cleanups: Array<() => void> = []

        root.querySelectorAll<HTMLElement>('.faq--container').forEach(container => {
            const question = container.querySelector<HTMLElement>('.bggle--question')
            const answer = container.querySelector<HTMLElement>('.reponse')

            if (!question || !answer) return

            answer.style.display = 'none'

            question.setAttribute('role', 'button')
            question.setAttribute('tabindex', '0')
            question.setAttribute('aria-expanded', 'false')

            const toggle = () => {
                const isOpen = answer.style.display !== 'none'

                answer.style.display = isOpen ? 'none' : 'block'
                question.setAttribute('aria-expanded', String(!isOpen))
                container.classList.toggle('is-open', !isOpen)
            }

            const onKeyDown = (event: KeyboardEvent) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault()
                    toggle()
                }
            }

            question.addEventListener('click', toggle)
            question.addEventListener('keydown', onKeyDown)

            cleanups.push(() => {
                question.removeEventListener('click', toggle)
                question.removeEventListener('keydown', onKeyDown)
            })
        })

        return () => cleanups.forEach(cleanup => cleanup())
    }, [html])

    return (
        <div ref={rootRef} className="hc-post-body">
            <div dangerouslySetInnerHTML={{ __html: html }} />
        </div>
    )
}