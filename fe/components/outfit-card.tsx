import React from "react";
import Image from "next/image";
import { CDN_ORGIN } from "@/lib/config";

export const PrimaryCard = ({ base }: any) => {
  return (
    <div className="aspect-[4/5] h-full overflow-hidden bg-white hover:lg:p-2 hover:p-1 rounded-lg">
      <div className="h-full w-full relative overflow-hidden bg-gray-200 rounded-lg">
        <Image
          src={`${CDN_ORGIN}${base.images[0].split("/")[1]}`}
          alt={base.name}
          fill
          className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
        />
        {/* Overlay Info for Base Product */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/70 to-transparent text-white">
          <p className="text-sm font-medium uppercase tracking-widest opacity-80">
            {base.brand}
          </p>
          <h2 className="text-2xl font-bold">{base.name}</h2>
          <p className="mt-1 text-lg font-semibold">₹{base.price}</p>
        </div>
      </div>
    </div>
  );
};
export const SecondaryCard = ({ item }: any) => {
  return (
    <div className="flex-1 flex p-2 hover:p-1 shadow-lg rounded-xl h-1/2 xl:h-full">
      <div
        key={item.id}
        className="aspect-[3/4] h-full relative rounded-xl overflow-hidden bg-gray-100 border border-gray-50 shadow-sm"
      >
        <Image
          src={`${CDN_ORGIN}${item.images[0].split("/")[1]}`}
          alt="Outfit item"
          fill
          className="object-cover w-full h-full hover:opacity-90 transition-opacity"
        />
      </div>
      <div className="px-4 py-4">
        <p className="text-sm font-bold uppercase tracking-wider text-gray-400">
          {item.brand}
        </p>
        <h3 className="text-md font-medium text-gray-800 line-clamp-2 leading-snug">
          {item.name}
        </h3>

        <div className="flex items-center gap-2 mt-2">
          <span className="text-base text-md font-bold text-gray-900">
            ₹{item.price}
          </span>
          {item.mrp > item.price && (
            <>
              <span className="text-xs text-gray-400 line-through">
                ₹{item.mrp}
              </span>
              <span className="text-xs font-bold text-green-600">
                ({Math.round(((item.mrp - item.price) / item.mrp) * 100)}% OFF)
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
