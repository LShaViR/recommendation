"use client";

import { useQuery } from "@tanstack/react-query";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { ProductCard} from "./product-card";
import axios from "axios"
import {BACKEND_URL} from "@/lib/config"

const ITEMS_PER_PAGE = 20;

export default function ProductGrid() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { push } = useRouter();

  // 1. Get current page from URL (?page=1)
  const currentPage = Number(searchParams.get("page")) || 1;

  // 2. React Query for fetching
  const { data, isLoading, isPlaceholderData } = useQuery({
    queryKey: ["products", currentPage],
    queryFn: async () => {
      const res = await axios.get(`${BACKEND_URL}/api/v1/products?skip=${currentPage*ITEMS_PER_PAGE}&limit=${ITEMS_PER_PAGE}`);
      console.log(res)
      return res.data
    },
    placeholderData: (previousData) => previousData, // Smooth transitions between pages
  });

  // 3. Update URL Parameters
  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams);
    params.set("page", newPage.toString());
    push(`${pathname}?${params.toString()}`);
  };

  if (isLoading) return <div className="grid gap-4 sm:grid-cols-4">Loading...</div>;

  return (
    <div className="flex flex-col gap-8">
      {/* Product Grid */}
      <div className="grid auto-rows-min gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {data?.data.map((product: any) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-center gap-4 border-t pt-6">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage <= 1 || isPlaceholderData}
          className="rounded-md border px-4 py-2 disabled:opacity-50"
        >
          Previous
        </button>

        <span className="text-sm font-medium">
          Page {currentPage} {data?.totalPages ? `of ${data.totalPages}` : ""}
        </span>

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={isPlaceholderData || (data && currentPage >= data.totalPages)}
          className="rounded-md border px-4 py-2 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
