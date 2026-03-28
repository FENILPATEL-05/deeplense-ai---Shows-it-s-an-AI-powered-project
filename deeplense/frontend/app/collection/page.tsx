"use client";

import { useState, useEffect, useCallback } from "react";
import { getAllImages, getImageUrl } from "@/lib/api";
import Lightbox from "@/components/Lightbox";
import type { SearchResult } from "@/types";
import Image from "next/image";

const PAGE_SIZE = 100;

export default function CollectionPage() {
  const [images, setImages] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lightboxResult, setLightboxResult] = useState<SearchResult | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setIsLoading(true);
        const data = await getAllImages(PAGE_SIZE, 0);
        setImages(data.results);
        setTotal(data.total);
      } catch (err: any) {
        setError(err.message || "Failed to load collection");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const loadMore = useCallback(async () => {
    try {
      setIsLoadingMore(true);
      const data = await getAllImages(PAGE_SIZE, images.length);
      setImages((prev) => [...prev, ...data.results]);
    } catch (err: any) {
      setError(err.message || "Failed to load more images");
    } finally {
      setIsLoadingMore(false);
    }
  }, [images.length]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 pt-8 pb-4 px-6">
        <div className="max-w-[1200px] mx-auto">
          <h1 className="text-2xl font-semibold text-[#202124] dark:text-[#e8eaed]">
            Collection
          </h1>
          {!isLoading && !error && (
            <p className="mt-1 text-sm text-[#5f6368] dark:text-[#9aa0a6]">
              {total} image{total !== 1 ? "s" : ""} indexed
            </p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 pb-6">
        <div className="max-w-[1200px] mx-auto">
          {/* Error */}
          {error && (
            <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Loading skeleton */}
          {isLoading && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {Array.from({ length: 20 }).map((_, i) => (
                <div
                  key={i}
                  className="rounded-2xl bg-[#f1f3f4] dark:bg-[#3c3c3c] aspect-square animate-pulse"
                />
              ))}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && images.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-[#5f6368] dark:text-[#9aa0a6]">
              <p className="text-lg font-medium">No images indexed yet</p>
              <p className="text-sm mt-1">Add images to the inbox folder to get started</p>
            </div>
          )}

          {/* Grid */}
          {!isLoading && images.length > 0 && (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {images.map((img) => (
                  <div
                    key={img.filename}
                    onClick={() => setLightboxResult(img)}
                    className="rounded-2xl overflow-hidden shadow-sm hover:shadow-md bg-white dark:bg-[#2d2d2d] cursor-pointer transition-all duration-200 hover:scale-[1.03] group"
                  >
                    <div className="relative aspect-square">
                      <Image
                        src={getImageUrl(img.filename)}
                        alt={img.filename}
                        fill
                        className="object-cover"
                        sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
                        unoptimized
                      />
                      {img.category && (
                        <span className="absolute top-2 left-2 px-2 py-0.5 rounded-full text-xs font-medium bg-black/50 text-white">
                          {img.category}
                        </span>
                      )}
                    </div>
                    <div className="px-3 py-2">
                      <p className="text-xs text-[#5f6368] dark:text-[#9aa0a6] truncate">
                        {img.filename}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Load More */}
              {images.length < total && (
                <div className="mt-8 flex justify-center">
                  <button
                    onClick={loadMore}
                    disabled={isLoadingMore}
                    className="px-6 py-2.5 rounded-full bg-[#1a73e8] text-white text-sm font-medium hover:bg-[#1557b0] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoadingMore
                      ? "Loading..."
                      : `Load more (${images.length} / ${total})`}
                  </button>
                </div>
              )}

              {images.length >= total && total > PAGE_SIZE && (
                <p className="mt-6 text-center text-sm text-[#5f6368] dark:text-[#9aa0a6]">
                  All {total} images loaded
                </p>
              )}
            </>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {lightboxResult && (
        <Lightbox result={lightboxResult} onClose={() => setLightboxResult(null)} />
      )}
    </div>
  );
}
