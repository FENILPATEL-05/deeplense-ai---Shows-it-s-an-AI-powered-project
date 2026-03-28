"use client";

import type { SearchFilters, FilterOptions } from "@/types";

interface FilterPanelProps {
  filters: SearchFilters;
  options: FilterOptions;
  onChange: (f: Partial<SearchFilters>) => void;
}

export default function FilterPanel({
  filters,
  options,
  onChange,
}: FilterPanelProps) {
  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags;
    if (currentTags.includes(tag)) {
      onChange({ tags: currentTags.filter((t) => t !== tag) });
    } else {
      onChange({ tags: [...currentTags, tag] });
    }
  };

  const handleCategoryChange = (category: string | null) => {
    onChange({ category: category === filters.category ? null : category });
  };

  const handleSortChange = (sort: "relevance" | "date") => {
    onChange({ sort_by: sort });
  };

  return (
    <div className="flex-shrink-0 px-6 py-3 border-t border-b border-[#e8eaed] dark:border-[#3c3c3c]">
      <div className="max-w-[800px] mx-auto">
        {/* Category row */}
        {options.categories.length > 0 && (
          <div className="mb-3 pb-3 border-b border-[#e8eaed] dark:border-[#3c3c3c]">
            <label className="block text-xs font-medium text-[#5f6368] dark:text-[#9aa0a6] mb-2">
              Category
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleCategoryChange(null)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                  filters.category === null
                    ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                    : "bg-[#f8f9fa] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                }`}
              >
                All
              </button>
              {options.categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleCategoryChange(cat)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                    filters.category === cat
                      ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                      : "bg-[#f8f9fa] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Top row: Tags and Sort */}
        <div className="flex flex-wrap items-center gap-4 mb-3">
          {/* Tags */}
          {options.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {options.tags.map((tag) => {
                const isSelected = filters.tags.includes(tag);
                return (
                  <button
                    key={tag}
                    onClick={() => handleTagToggle(tag)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                      isSelected
                        ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                        : "bg-[#f8f9fa] dark:bg-[#3c3c3c] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#4a4a4a]"
                    }`}
                  >
                    {tag}
                  </button>
                );
              })}
            </div>
          )}

          {/* Sort */}
          <div className="flex ml-auto items-center gap-3">
            <div className="flex border border-[#e8eaed] dark:border-[#3c3c3c] rounded-full overflow-hidden">
            <button
              onClick={() => handleSortChange("relevance")}
              className={`px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
                filters.sort_by === "relevance"
                  ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                  : "bg-white dark:bg-[#2d2d2d] text-[#5f6368] dark:text-[#9aa0a6]"
              }`}
            >
              Relevance
            </button>
            <button
              onClick={() => handleSortChange("date")}
              className={`px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
                filters.sort_by === "date"
                  ? "bg-[#1a73e8] dark:bg-[#8ab4f8] text-white dark:text-[#1f1f1f]"
                  : "bg-white dark:bg-[#2d2d2d] text-[#5f6368] dark:text-[#9aa0a6]"
              }`}
            >
              Newest
            </button>
            </div>
          </div>
        </div>

        {/* Accuracy threshold slider */}
        <div className="flex items-center gap-4">
          <label className="text-xs font-medium text-[#5f6368] dark:text-[#9aa0a6] whitespace-nowrap">
            Match Quality:
          </label>
          <input
            type="range"
            min="0.20"
            max="0.60"
            step="0.02"
            value={Math.min(Math.max(filters.score_threshold, 0.20), 0.60)}
            onChange={(e) => onChange({ score_threshold: parseFloat(e.target.value) })}
            className="flex-1 h-2 bg-[#e8eaed] dark:bg-[#3c3c3c] rounded-lg appearance-none cursor-pointer slider"
            style={{
              background: `linear-gradient(to right, #1a73e8 0%, #1a73e8 ${((Math.min(Math.max(filters.score_threshold, 0.20), 0.60) - 0.20) / 0.40 * 100).toFixed(0)}%, #e8eaed ${((Math.min(Math.max(filters.score_threshold, 0.20), 0.60) - 0.20) / 0.40 * 100).toFixed(0)}%, #e8eaed 100%)`
            }}
          />
          <span className="text-xs font-medium text-[#1a73e8] dark:text-[#8ab4f8] min-w-[3rem]">
            {filters.score_threshold.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
}
