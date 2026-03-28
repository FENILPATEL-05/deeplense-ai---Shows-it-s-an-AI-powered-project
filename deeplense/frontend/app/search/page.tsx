"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { useSearch } from "@/hooks/useSearch";
import SearchBar from "@/components/SearchBar";
import ImageUpload from "@/components/ImageUpload";
import FilterButton from "@/components/FilterButton";
import ResultsGrid from "@/components/ResultsGrid";
import Skeleton from "@/components/Skeleton";
import Lightbox from "@/components/Lightbox";
import type { SearchResult } from "@/types";

export default function SearchPage() {
  const {
    query,
    results,
    total,
    isLoading,
    error,
    filters,
    filterOptions,
    uploadedFile,
    uploadedPreview,
    searchByText,
    searchByImage,
    updateFilters,
    clearSearch,
  } = useSearch();

  const [lightboxResult, setLightboxResult] = useState<SearchResult | null>(
    null
  );

  const hasResults = results.length > 0;
  const hasSearched = query.trim() !== "" || uploadedPreview !== null;

  return (
    <div className="flex flex-col h-full">
      {/* Search Bar Area */}
      <div className="flex-shrink-0 pt-8 pb-4 px-6">
        <div className="max-w-[800px] mx-auto">
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <SearchBar onSearch={searchByText} isLoading={isLoading} />
            </div>
            <ImageUpload onUpload={searchByImage} isLoading={isLoading} />
            <FilterButton
              filters={filters}
              options={filterOptions}
              onChange={updateFilters}
            />
          </div>

          {/* Uploaded Image Preview */}
          {uploadedPreview && uploadedFile && (
            <div className="mt-3 flex items-center gap-3 px-2">
              <img
                src={uploadedPreview}
                alt="Uploaded"
                className="w-10 h-10 rounded-lg object-cover border border-[#e8eaed] dark:border-[#3c3c3c]"
              />
              <span className="text-sm text-[#5f6368] dark:text-[#9aa0a6] truncate max-w-[200px]">
                {uploadedFile.name}
              </span>
              <button
                onClick={clearSearch}
                className="text-xs text-[#5f6368] dark:text-[#9aa0a6] hover:text-[#202124] dark:hover:text-[#e8eaed] transition-all duration-200"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Filter Panel removed - now using FilterButton in search bar */}

      {/* Error */}
      {error && (
        <div className="px-6 py-3">
          <div className="max-w-[800px] mx-auto text-red-500 text-sm bg-red-50 dark:bg-red-900/20 px-4 py-2 rounded-xl">
            {error}
          </div>
        </div>
      )}

      {/* Results Area */}
      <div className="flex-1 overflow-auto px-6 pb-6">
        {isLoading ? (
          <Skeleton />
        ) : hasResults ? (
          <ResultsGrid
            results={results}
            total={total}
            onCardClick={setLightboxResult}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 rounded-full bg-[#f8f9fa] dark:bg-[#2d2d2d] flex items-center justify-center mb-6">
              <Search className="w-8 h-8 text-[#5f6368] dark:text-[#9aa0a6]" />
            </div>
            <h2 className="text-lg font-medium text-[#202124] dark:text-[#e8eaed] mb-2">
              {hasSearched ? "No results found" : "Search for images or upload a photo"}
            </h2>
            <p className="text-sm text-[#5f6368] dark:text-[#9aa0a6]">
              {hasSearched
                ? "Try different keywords or filters"
                : "Results will appear here"}
            </p>
          </div>
        )}
      </div>

      {/* Lightbox */}
      <Lightbox result={lightboxResult} onClose={() => setLightboxResult(null)} />
    </div>
  );
}
