import { useBrands, useCategories, useEffects } from '@/hooks/useApi'
import type { MenuNode } from '@/components/layout/navbar/NavFlyoutItem'
import type { Category } from '@/types'

// Recursively turns a Category (with however many levels of `children`
// the API sends back) into a MenuNode, so subcategories nest to
// whatever depth the backend actually has.
function categoryToNode(category: Category): MenuNode {
    return {
        label: category.name,
        href: category.is_key ? `/shop/categories/${category.slug}` : `/shop/collections/${category.slug}`,
        children: category.children?.length
            ? category.children.map(categoryToNode)
            : undefined,
    }
}

// Builds the full "Categories" dropdown tree: real category hierarchy,
// plus a "Brands" branch and an "Effects" branch, each expanding into
// their own live list. Shared by the desktop flyout and mobile accordion
// so both stay in sync automatically.
export function useCategoriesMenuTree() {
    const { data: categories, isLoading: categoriesLoading } = useCategories()
    const { data: brands }  = useBrands()
    const { data: effects } = useEffects()

    const categoryNodes: MenuNode[] = (categories ?? []).map(categoryToNode)

    const departmentsNode: MenuNode | null = categoryNodes.length
        ? {
            label: 'Departments',
            children: categoryNodes,
        }
        : null

    const brandNode: MenuNode | null = brands?.length
        ? {
            label: 'Brands',
            children: brands.map(b => ({
                label: b.name,
                href: `/shop/brands/${b.slug}`,
            })),
        }
        : null

    const effectNode: MenuNode | null = effects?.length
        ? {
            label: 'Effects',
            children: effects.map(e => ({
                label: e.name,
                href: `/shop/products?effect=${e.slug}`,
            })),
        }
        : null

    const rootNodes: MenuNode[] = [
        ...(departmentsNode ? [departmentsNode] : []),
        ...(brandNode ? [brandNode] : []),
        ...(effectNode ? [effectNode] : []),
    ]

    return { rootNodes, isLoading: categoriesLoading }
}
