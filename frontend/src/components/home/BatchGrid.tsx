import { JarCard } from '@/components/home/JarCard'
import { Reveal } from '@/components/home/Reveal'
import { getProducts } from '@/lib/catalog.server'
import { toJarProduct } from '@/lib/jarProduct'

// Pulled from the real catalog (recently added products with real lab
// data) instead of hardcoded placeholder jars — every claim here (THC,
// terpene, COA availability) traces back to an actual product/variant
// record, and each card links straight to that product's page.
export async function BatchGrid() {
    const { results } = await getProducts({ ordering: '-created_at', page_size: 3 })
    if (results.length === 0) return null

    const batch = results.map(toJarProduct)

    return (
        <section id="batch" className="bg-hc-paper px-7 py-24">
            <div className="mx-auto max-w-[1180px]">
                <Reveal className="mb-11 flex flex-wrap items-end justify-between gap-6">
                    <div>
                        <div className="inline-flex items-center gap-2 font-hc-mono text-xs uppercase tracking-[0.12em] text-hc-sage-dim before:h-px before:w-3.5 before:bg-current before:opacity-50">
                            Newest to the menu
                        </div>
                        <h2 className="mt-2.5 max-w-[520px] font-hc-display text-[28px] font-normal sm:text-4xl">
                            Recently added, lab-tested batches
                        </h2>
                    </div>
                    <p className="max-w-[320px] text-sm text-hc-ink-soft">
                        Every product page links to its real certificate of analysis when one is on file.
                    </p>
                </Reveal>

                <div className="grid grid-cols-1 gap-6.5 md:grid-cols-3">
                    {batch.map((product, i) => (
                        <Reveal key={product.sku} delay={i * 80}>
                            <JarCard product={product} interactive />
                        </Reveal>
                    ))}
                </div>
            </div>
        </section>
    )
}
