import Link from "next/link";

export default function Page() {
  return (
    <div className="h-screen w-screen flex flex-col space-y-4 justify-center items-center bg-[#010101]">
      <h1 className="text-5xl text-white font-bold">
        Outfit recommedation system
      </h1>
      <Link href="/catalog" className="text-3xl text-white bg-[#191919] p-8">
        Inter into the application
      </Link>
    </div>
  );
}
