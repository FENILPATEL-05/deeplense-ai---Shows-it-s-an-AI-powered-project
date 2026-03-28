"use client";

import Image from "next/image";
import type { SearchResult } from "@/types";
import { getImageUrl } from "@/lib/api";

interface ImageCardProps {
  result: SearchResult;
  onClick: (result: SearchResult) => void;
}

function getScoreBadgeColor(score: number): string {
  const pct = score * 100;
  if (pct > 85) return "bg-[#34a853]/80 text-white";
  if (pct >= 65) return "bg-[#fbbc04]/80 text-[#202124]";
  return "bg-[#5f6368]/60 text-white";
}

export default function ImageCard({ result, onClick }: ImageCardProps) {
  const scorePercent = Math.round(result.score * 100);

  return (
    <div
      onClick={() => onClick(result)}
      className="rounded-2xl overflow-hidden shadow-sm hover:shadow-md bg-white dark:bg-[#2d2d2d] cursor-pointer transition-all duration-200 hover:scale-[1.03] group"
    >
      <div className="relative aspect-square">
        <Image
          src={getImageUrl(result.filename)}
          alt={result.filename}
          fill
          className="object-cover"
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
          unoptimized
        />
        {/* Score Badge */}
        <span
          className={`absolute top-2 right-2 px-2 py-0.5 rounded-full text-xs font-medium ${getScoreBadgeColor(
            result.score
          )}`}
        >
          {scorePercent}%
        </span>
      </div>
      <div className="px-3 py-2">
        <p className="text-xs text-[#5f6368] dark:text-[#9aa0a6] truncate">
          {result.filename}
        </p>
      </div>
    </div>
  );
}
