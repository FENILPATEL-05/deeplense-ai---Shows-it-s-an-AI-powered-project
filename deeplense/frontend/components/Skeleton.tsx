"use client";

export default function Skeleton() {
  return (
    <div className="py-4">
      {/* Header skeleton */}
      <div className="h-4 w-24 skeleton-shimmer rounded-full mb-4" />
      {/* Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="rounded-2xl overflow-hidden">
            <div className="aspect-square skeleton-shimmer" />
            <div className="px-3 py-2">
              <div className="h-3 w-3/4 skeleton-shimmer rounded-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
