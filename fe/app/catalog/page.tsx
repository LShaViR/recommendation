import { ProductCard } from "@/components/product-card";
import ProductGrid from "@/components/product-list";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";

const Catalog = () => {
  return (
    <div className="h-full w-full flex flex-col items-center">
      <header className="bg-background sticky z-10 top-0 flex h-16 shrink-0 items-center gap-2 border-b px-4 w-full">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Lucky Rathore</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>
      <main className="flex flex-1 flex-col gap-4 p-4 max-w-5xl w-full">
        <ProductGrid />
      </main>
    </div>
  );
};

export default Catalog;
