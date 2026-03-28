"use client";

import { useState, useRef, KeyboardEvent, ChangeEvent } from "react";
import { Search, X } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    setValue(v);
    onSearch(v);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      onSearch(value);
    }
  };

  const handleClear = () => {
    setValue("");
    onSearch("");
    inputRef.current?.focus();
  };

  return (
    <div className="relative w-full max-w-[720px]">
      <div
        className={`flex items-center rounded-full border bg-white dark:bg-[#2d2d2d] px-5 py-3 transition-all duration-200 ${
          "border-[#e8eaed] dark:border-[#3c3c3c] focus-within:border-[#1a73e8] dark:focus-within:border-[#8ab4f8] focus-within:shadow-md"
        }`}
      >
        <Search className="w-5 h-5 text-[#5f6368] dark:text-[#9aa0a6] flex-shrink-0 mr-3" />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Search 5000+ images…"
          className="flex-1 bg-transparent outline-none text-[#202124] dark:text-[#e8eaed] placeholder:text-[#5f6368] dark:placeholder:text-[#9aa0a6] text-base"
        />
        {value && (
          <button
            onClick={handleClear}
            className="ml-2 p-1 rounded-full hover:bg-[#f8f9fa] dark:hover:bg-[#3c3c3c] transition-all duration-200"
          >
            <X className="w-4 h-4 text-[#5f6368] dark:text-[#9aa0a6]" />
          </button>
        )}
      </div>

      {/* Loading bar */}
      {isLoading && (
        <div className="absolute bottom-0 left-5 right-5 h-0.5 overflow-hidden rounded-full">
          <div className="h-full w-1/2 bg-[#1a73e8] dark:bg-[#8ab4f8] loading-bar rounded-full" />
        </div>
      )}
    </div>
  );
}
