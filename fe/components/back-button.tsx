import { Button } from "@base-ui/react";
import { useRouter } from "next/navigation";

export const BackButton = () => {
  const router = useRouter();
  return (
    <Button
      className="bg-black rounded-md text-white font-bold px-2 py-0.5 text-sm"
      onClick={() => router.back()}
    >
      Back
    </Button>
  );
};
