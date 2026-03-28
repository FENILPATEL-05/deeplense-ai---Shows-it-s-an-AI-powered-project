"use client";

import { useState } from "react";
import type { SearchFilters, FilterOptions } from "@/types";

interface FilterButtonProps {
  filters: SearchFilters;
  options: FilterOptions;
  onChange: (f: Partial<SearchFilters>) => void;
}

export default function FilterButton({
  filters,
  options,
  onChange,
}: FilterButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleCategoryChange = (category: string | null) => {
    onChange({ category: category === filters.category ? null : category });
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags;
    if (currentTags.includes(tag)) {
      onChange({ tags: currentTags.filter((t) => t !== tag) });
    } else {
      onChange({ tags: [...currentTags, tag] });
    }
  };

  const handleSortChange = (sort: "relevance" | "date") => {
    onChange({ sort_by: sort });
  };

  const hasActiveFilters =
    filters.category !== null ||
    filters.tags.length > 0 ||
    filters.score_threshold !== 0.2 ||
    filters.sort_by !== "relevance";

  return (
    <div className="relative">
      {/* Filter Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
          isOpen || hasActiveFilters
            ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
            : "bg-[#f8f9fa] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
        }`}
      >
        <span>⚙️ Filter</span>
        {hasActiveFilters && (
          <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-red-500 text-white rounded-full">
            1
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-12 left-0 z-50 w-80 bg-white dark:bg-[#2d2d2d] rounded-lg shadow-lg border border-[#e8eaed] dark:border-[#3c3c3c] p-4">
          {/* Category Section */}
          {options.categories.length > 0 && (
            <div className="mb-4 pb-4 border-b border-[#e8eaed] dark:border-[#3c3c3c]">
              <label className="block text-sm font-semibold text-[#202124] dark:text-[#e8eaed] mb-3">
                📁 Category
              </label>
              <div className="space-y-2">
                <button
                  onClick={() => handleCategoryChange(null)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm transition-all duration-200 ${
                    filters.category === null
                      ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                      : "hover:bg-[#f0f0f0] dark:hover:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6]"
                  }`}
                >
                  ✓ All Categories
                </button>
                {options.categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => handleCategoryChange(cat)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-all duration-200 capitalize ${
                      filters.category === cat
                        ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                        : "hover:bg-[#f0f0f0] dark:hover:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6]"
                    }`}
                  >
                    {filters.category === cat ? "✓ " : "  "} {cat}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Match Quality Section */}
          <div className="mb-4 pb-4 border-b border-[#e8eaed] dark:border-[#3c3c3c]">
            <label className="block text-sm font-semibold text-[#202124] dark:text-[#e8eaed] mb-3">
              🎯 Match Quality
            </label>
            <div className="space-y-3">
              <input
                type="range"
                min="0.20"
                max="0.60"
                step="0.02"
                value={Math.min(Math.max(filters.score_threshold, 0.2), 0.6)}
                onChange={(e) =>
                  onChange({ score_threshold: parseFloat(e.target.value) })
                }
                className="w-full h-2 bg-[#e8eaed] dark:bg-[#3c3c3c] rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #1a73e8 0%, #1a73e8 ${(
                    ((Math.min(Math.max(filters.score_threshold, 0.2), 0.6) - 0.2) /
                      0.4) *
                    100
                  ).toFixed(0)}%, #e8eaed ${(
                    ((Math.min(Math.max(filters.score_threshold, 0.2), 0.6) - 0.2) /
                      0.4) *
                    100
                  ).toFixed(0)}%, #e8eaed 100%)`,
                }}
              />
              <div className="flex justify-between items-center text-xs">
                <span className="text-[#5f6368] dark:text-[#9aa0a6]">
                  Loose (0.20)
                </span>
                <span className="font-semibold text-[#1a73e8] dark:text-[#8ab4f8]">
                  {filters.score_threshold.toFixed(2)}
                </span>
                <span className="text-[#5f6368] dark:text-[#9aa0a6]">
                  Strict (0.60)
                </span>
              </div>
            </div>
          </div>

          {/* Tags Section */}
          {options.tags.length > 0 && (
            <div className="mb-4 pb-4 border-b border-[#e8eaed] dark:border-[#3c3c3c]">
              <label className="block text-sm font-semibold text-[#202124] dark:text-[#e8eaed] mb-3">
                🏷️ Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {options.tags.map((tag) => {
                  const isSelected = filters.tags.includes(tag);
                  return (
                    <button
                      key={tag}
                      onClick={() => handleTagToggle(tag)}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                        isSelected
                          ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                          : "bg-[#f0f0f0] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                      }`}
                    >
                      {tag}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Sort Section */}
          <div className="mb-2">
            <label className="block text-sm font-semibold text-[#202124] dark:text-[#e8eaed] mb-3">
              📊 Sort By
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => handleSortChange("relevance")}
                className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  filters.sort_by === "relevance"
                    ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                    : "bg-[#f0f0f0] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                }`}
              >
                Relevance
              </button>
              <button
                onClick={() => handleSortChange("date")}
                className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  filters.sort_by === "date"
                    ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                    : "bg-[#f0f0f0] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                }`}
              >
                Newest
              </button>
            </div>
          </div>

          {/* Close hint */}
          <div className="mt-4 text-center text-xs text-[#5f6368] dark:text-[#9aa0a6]">
            Click Filter button to close
          </div>
        </div>
      )}

      {/* Close on click outside */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
