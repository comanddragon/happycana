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

        root
            .querySelectorAll<HTMLElement>(
                '.bggle_table-of-content .bggle--anchor',
            )
            .forEach(link => {
                const href = link.getAttribute('href')

                if (!href?.startsWith('#')) return

                const id = href.slice(1)

                if (!id) return

                const target = root.querySelector<HTMLElement>(
                    `[id="${CSS.escape(id)}"]`,
                )

                if (!target) return

                const tagName = target.tagName.toLowerCase()

                // Remove any existing TOC level classes.
                link.classList.remove(
                    'toc-level-2',
                    'toc-level-3',
                    'toc-level-4',
                    'toc-level-5',
                    'toc-level-6',
                )

                // Assign a level based on the actual heading.
                if (/^h[2-6]$/.test(tagName)) {
                    link.classList.add(
                        `toc-level-${tagName.substring(1)}`,
                    )
                }
            })

        // ─────────────────────────────────────────────
        // FAQ ACCORDION
        // ─────────────────────────────────────────────

        root.querySelectorAll<HTMLElement>('.faq--container').forEach(
            container => {
                const question =
                    container.querySelector<HTMLElement>(
                        '.bggle--question',
                    )

                const answer =
                    container.querySelector<HTMLElement>('.reponse')

                if (!question || !answer) return

                // Collapsed by default.
                answer.style.display = 'none'

                question.setAttribute('role', 'button')
                question.setAttribute('tabindex', '0')
                question.setAttribute('aria-expanded', 'false')

                const toggle = () => {
                    const isOpen = answer.style.display !== 'none'

                    answer.style.display = isOpen ? 'none' : 'block'

                    question.setAttribute(
                        'aria-expanded',
                        String(!isOpen),
                    )

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
            },
        )

        return () => {
            cleanups.forEach(cleanup => cleanup())
        }
    }, [html])

    return (
        <div ref={rootRef} className="hc-post-body mt-10">
            <div dangerouslySetInnerHTML={{ __html: html }} />
        </div>
    )
}