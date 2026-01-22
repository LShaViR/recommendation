import Image from "next/image";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { CDN_ORGIN } from "@/lib/config";
import Link from "next/link";

// Define the shape of your product data based on the JSON
interface ProductProps {
  product:
    | {
        name: string;
        brand: string;
        price: number;
        mrp: number;
        primary_colour: string;
        images: string[];
      }
    | any;
}

export const ProductCard = ({ product }: ProductProps) => {
  const hasDiscount = product.mrp > product.price;

  return (
    <Link
      href={
        product.sub_category == "Topwear" ? `/outfit/${product.id}` : "/catalog"
      }
    >
      <div className="bg-muted/50 w-full aspect-[5/8] group rounded-sm">
        <Card className="h-full w-full p-1 rounded-xs gap-0 overflow-hidden flex flex-col">
          <CardContent className="p-0 transition-all duration-200 group-hover:p-1">
            <div className="aspect-4/5 relative overflow-hidden rounded-xs">
              {/* Using a placeholder if image path is just a string from JSON */}
              <Image
                src={`${CDN_ORGIN}${product.images[0].split("/")[1]}`}
                alt={product.name}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </div>
          </CardContent>

          <CardFooter className="flex-1 px-2 py-3">
            <div className="w-full flex flex-col gap-1">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {product.brand}
                </span>
                <h3 className="text-sm font-medium leading-tight line-clamp-1">
                  {product.name}
                </h3>
              </div>

              <div className="flex items-center gap-2 mt-auto">
                <span className="text-base font-bold text-primary">
                  ₹{product.price}
                </span>
                {hasDiscount && (
                  <span className="text-xs text-muted-foreground line-through">
                    ₹{product.mrp}
                  </span>
                )}
              </div>
            </div>
          </CardFooter>
        </Card>
      </div>
    </Link>
  );
};
