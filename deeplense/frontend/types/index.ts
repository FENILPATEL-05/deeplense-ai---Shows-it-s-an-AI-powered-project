export interface SearchResult {
  filename: string;
  path: string;
  score: number;
  category: string | null;
  tags: string[];
  uploaded_at: string;
}

export interface SearchResponse {
  total: number;
  results: SearchResult[];
}

export interface FilterOptions {
  categories: string[];
  tags: string[];
}

export interface SearchFilters {
  category: string | null;
  tags: string[];
  sort_by: "relevance" | "date";
  limit: number;
  score_threshold: number;
}
