"use client";

import { useEffect, useCallback } from "react";
import { X } from "lucide-react";
import type { SearchResult } from "@/types";
import { getImageUrl } from "@/lib/api";

interface LightboxProps {
  result: SearchResult | null;
  onClose: () => void;
}

export default function Lightbox({ result, onClose }: LightboxProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (result) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [result, handleKeyDown]);

  if (!result) return null;

  const scorePercent = Math.round(result.score * 100);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-all duration-200 z-10"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      {/* Content */}
      <div
        className="flex flex-col items-center max-w-[90vw] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image */}
        <img
          src={getImageUrl(result.filename)}
          alt={result.filename}
          className="max-w-full max-h-[75vh] object-contain rounded-xl"
        />

        {/* Info Bar */}
        <div className="mt-4 w-full max-w-xl bg-white/10 backdrop-blur-md rounded-2xl px-6 py-4 text-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-base font-medium truncate mr-4">
              {result.filename}
            </h3>
            <span className="text-sm font-medium text-[#8ab4f8] flex-shrink-0">
              {scorePercent}% match
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm text-white/70">
            {result.category && (
              <span className="px-2.5 py-0.5 rounded-full bg-white/10 text-xs">
                {result.category}
              </span>
            )}
            {result.tags.map((tag) => (
              <span
                key={tag}
                className="px-2.5 py-0.5 rounded-full bg-white/10 text-xs"
              >
                {tag}
              </span>
            ))}
            {result.uploaded_at && (
              <span className="text-xs text-white/50 ml-auto">
                {new Date(result.uploaded_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
