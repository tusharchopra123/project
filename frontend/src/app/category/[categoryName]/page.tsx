"use client";

import CategoryView from "@/components/CategoryView";

export default function CategoryPage({ params }: { params: Promise<{ categoryName: string }> }) {
    return <CategoryView params={params} />;
}
