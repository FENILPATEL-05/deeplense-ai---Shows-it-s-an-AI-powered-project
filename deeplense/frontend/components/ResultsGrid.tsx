"use client";

import type { SearchResult } from "@/types";
import ImageCard from "./ImageCard";

interface ResultsGridProps {
  results: SearchResult[];
  total: number;
  onCardClick: (result: SearchResult) => void;
}

export default function ResultsGrid({
  results,
  total,
  onCardClick,
}: ResultsGridProps) {
  return (
    <div className="py-4">
      <p className="text-sm text-[#5f6368] dark:text-[#9aa0a6] mb-4">
        {total} result{total !== 1 ? "s" : ""}
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {results.map((result, idx) => (
          <ImageCard key={`${result.filename}-${idx}`} result={result} onClick={onCardClick} />
        ))}
      </div>
    </div>
  );
}
