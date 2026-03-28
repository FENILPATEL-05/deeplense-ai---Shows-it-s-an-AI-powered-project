"use client";

import { useRef } from "react";
import { Upload, Loader2 } from "lucide-react";

interface ImageUploadProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

export default function ImageUpload({ onUpload, isLoading }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      e.target.value = "";
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
      />
      <button
        onClick={handleClick}
        disabled={isLoading}
        className="flex items-center gap-2 px-5 py-3 rounded-full border border-[#e8eaed] dark:border-[#3c3c3c] bg-white dark:bg-[#2d2d2d] text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#f8f9fa] dark:hover:bg-[#3c3c3c] transition-all duration-200 text-sm font-medium whitespace-nowrap disabled:opacity-50"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Upload className="w-4 h-4" />
        )}
        Upload image
      </button>
    </>
  );
}
