"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import type {
  SearchResult,
  SearchResponse,
  SearchFilters,
  FilterOptions,
} from "@/types";
import {
  searchByText,
  searchByImage,
  getFilters as fetchFilters,
} from "@/lib/api";

const DEFAULT_FILTERS: SearchFilters = {
  category: null,
  tags: [],
  sort_by: "relevance",
  limit: 50,
  score_threshold: 0.20,
};

export function useSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    categories: [],
    tags: [],
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedPreview, setUploadedPreview] = useState<string | null>(null);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const filterDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastQueryRef = useRef("");
  const lastModeRef = useRef<"text" | "image">("text");

  useEffect(() => {
    fetchFilters()
      .then(setFilterOptions)
      .catch(() => {});
  }, []);

  const doTextSearch = useCallback(
    async (q: string, f: SearchFilters) => {
      if (!q.trim()) return;
      setIsLoading(true);
      setError(null);
      try {
        const data: SearchResponse = await searchByText(q, f);
        setResults(data.results);
        setTotal(data.total);
      } catch (err: any) {
        setError(err.message);
        setResults([]);
        setTotal(0);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const doImageSearch = useCallback(
    async (file: File, f: SearchFilters) => {
      setIsLoading(true);
      setError(null);
      try {
        const data: SearchResponse = await searchByImage(file, f);
        setResults(data.results);
        setTotal(data.total);
      } catch (err: any) {
        setError(err.message);
        setResults([]);
        setTotal(0);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const handleSearchByText = useCallback(
    (q: string) => {
      setQuery(q);
      lastQueryRef.current = q;
      lastModeRef.current = "text";

      if (uploadedPreview) {
        URL.revokeObjectURL(uploadedPreview);
        setUploadedPreview(null);
        setUploadedFile(null);
      }

      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        doTextSearch(q, filters);
      }, 300);
    },
    [filters, doTextSearch, uploadedPreview]
  );

  const handleSearchByImage = useCallback(
    (file: File) => {
      setUploadedFile(file);
      const preview = URL.createObjectURL(file);
      setUploadedPreview(preview);
      lastModeRef.current = "image";
      setQuery("");
      doImageSearch(file, filters);
    },
    [filters, doImageSearch]
  );

  const updateFilters = useCallback(
    (partial: Partial<SearchFilters>) => {
      setFilters((prev) => {
        const next = { ...prev, ...partial };

        // Debounce filter changes to prevent rapid API calls from slider
        if (filterDebounceRef.current) {
          clearTimeout(filterDebounceRef.current);
        }

        filterDebounceRef.current = setTimeout(() => {
          if (lastModeRef.current === "text" && lastQueryRef.current.trim()) {
            doTextSearch(lastQueryRef.current, next);
          } else if (lastModeRef.current === "image" && uploadedFile) {
            doImageSearch(uploadedFile, next);
          }
        }, 500);

        return next;
      });
    },
    [doTextSearch, doImageSearch, uploadedFile]
  );

  const clearSearch = useCallback(() => {
    setQuery("");
    setResults([]);
    setTotal(0);
    setError(null);
    setFilters(DEFAULT_FILTERS);
    if (uploadedPreview) URL.revokeObjectURL(uploadedPreview);
    setUploadedFile(null);
    setUploadedPreview(null);
    lastQueryRef.current = "";
    lastModeRef.current = "text";
  }, [uploadedPreview]);

  return {
    query,
    results,
    total,
    isLoading,
    error,
    filters,
    filterOptions,
    uploadedFile,
    uploadedPreview,
    searchByText: handleSearchByText,
    searchByImage: handleSearchByImage,
    updateFilters,
    clearSearch,
  };
}
