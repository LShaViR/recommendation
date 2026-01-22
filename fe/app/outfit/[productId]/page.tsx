"use client";

import { BackButton } from "@/components/back-button";
import { PrimaryCard, SecondaryCard } from "@/components/outfit-card";
import { BACKEND_URL } from "@/lib/config";
import { useAuth } from "@/provider/authProvider";
import { Button } from "@base-ui/react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

const fetchRecommendations = async (productId: string, token: string) => {
  const data = await axios.get(
    `${BACKEND_URL}/api/v1/recommendation/${productId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    },
  );

  return data.data;
};
const Page = () => {
  const { productId } = useParams();
  const { token } = useAuth();
  const router = useRouter();

  const [outfit, setOutfit] = useState(0);

  if (!productId || !token) {
    router.replace("/");
    return;
  }
  const { data, isLoading, isError, error } = useQuery({
    // The queryKey ensures the data refetches when productId changes
    queryKey: ["recommendations", productId],
    queryFn: () => fetchRecommendations(productId, token),
    // Only run the query if we have the required values
    enabled: !!productId && !!token,
  });

  if (isLoading || !data) {
    return <div className="flex justify-center items-center">Loading...</div>;
  }
  const outfits = data.outfits;
  const { base, bottom, shoe, accessory } = outfits[outfit];

  const total = base.price + bottom.price + shoe.price + accessory.price;
  return (
    <div className=" h-screen w-screen flex flex-col">
      <div className="flex-1 w-screen lg:flex lg:flex-row overflow-auto no-scrollbar">
        <div className="h-full flex justify-center items-center p-2">
          <PrimaryCard base={base} />
        </div>
        <div className="h-full lg:flex-1 xl:flex flex-col lg:overflow-auto no-scrollbar">
          <div className="h-full flex flex-col xl:h-1/2 xl:flex-row xl:flex-1">
            <SecondaryCard item={base} /> <SecondaryCard item={bottom} />
          </div>
          <div className="h-full flex flex-col xl:h-1/2 xl:flex-row xl:flex-1">
            <SecondaryCard item={shoe} /> <SecondaryCard item={accessory} />
          </div>
        </div>
      </div>
      <div className="h-10 w-full flex justify-between p-2 shadow-xl border-t border-gray-300">
        <div>
          <BackButton />
        </div>
        <div className="space-x-3">
          <Button
            className="bg-gray-200 rounded-md"
            onClick={() =>
              setOutfit((prev) => Math.max(prev - 1, 0) % outfits.length)
            }
          >
            <ChevronsLeft />
          </Button>
          <Button
            className="bg-gray-200 rounded-md"
            onClick={() => setOutfit((prev) => (prev + 1) % outfits.length)}
          >
            <ChevronsRight />
          </Button>
        </div>
        <div className="flex items-end gap-2">
          <div className="text-sm xl:text-md">Total:</div>
          <div className="text-md xl:text-lg">₹{total}</div>
        </div>
      </div>
    </div>
  );
};

export default Page;
