<<<<<<< HEAD
import { CRYPTO_COLORS, CRYPTO_SYMBOLS } from "@/lib/utils"

interface CryptoIconProps {
  crypto: string
  size?: "sm" | "md" | "lg"
}

const sizes = {
  sm: "w-6 h-6 text-xs",
  md: "w-8 h-8 text-sm",
  lg: "w-12 h-12 text-base",
}

export function CryptoIcon({ crypto, size = "md" }: CryptoIconProps) {
  const color = CRYPTO_COLORS[crypto] || "#888"
  const symbol = CRYPTO_SYMBOLS[crypto] || crypto.slice(0, 3).toUpperCase()

  return (
    <div
      className={`${sizes[size]} rounded-full flex items-center justify-center font-bold text-white`}
=======
import Image from "next/image";
import { CRYPTO_COLORS, CRYPTO_SYMBOLS } from "@/lib/utils";

interface CryptoIconProps {
  crypto: string;
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: { width: 24, height: 24, className: "w-6 h-6" },
  md: { width: 32, height: 32, className: "w-8 h-8" },
  lg: { width: 48, height: 48, className: "w-12 h-12" },
};

// Map crypto IDs to local or external image URLs
// Local logos take priority over external URLs
const CRYPTO_IMAGES: Record<string, string> = {
  bitcoin: "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
  ethereum: "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
  binancecoin:
    "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png",
  solana: "https://assets.coingecko.com/coins/images/4128/small/solana.png",
  hyperliquid: "/crypto-logos/hyperliquid.png", // Local logo
  ripple:
    "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png",
  tether: "https://assets.coingecko.com/coins/images/325/small/Tether.png",
};

export function CryptoIcon({ crypto, size = "md" }: CryptoIconProps) {
  const sizeConfig = sizes[size];
  const imageUrl = CRYPTO_IMAGES[crypto];
  const color = CRYPTO_COLORS[crypto] || "#888";
  const symbol = CRYPTO_SYMBOLS[crypto] || crypto.slice(0, 3).toUpperCase();

  // If we have a real image URL, use it
  if (imageUrl) {
    return (
      <div className={`${sizeConfig.className} relative flex-shrink-0`}>
        <Image
          src={imageUrl}
          alt={crypto}
          width={sizeConfig.width}
          height={sizeConfig.height}
          className="rounded-full"
          unoptimized={imageUrl.startsWith("http")} // Only unoptimized for external URLs
        />
      </div>
    );
  }

  // Fallback to colored circle with letter
  return (
    <div
      className={`${sizeConfig.className} rounded-full flex items-center justify-center font-bold text-white flex-shrink-0`}
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
      style={{ backgroundColor: color }}
    >
      {symbol.slice(0, 1)}
    </div>
<<<<<<< HEAD
  )
=======
  );
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
}
