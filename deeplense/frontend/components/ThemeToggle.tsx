"use client";

import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";
import { useEffect, useState } from "react";

interface ThemeToggleProps {
  collapsed?: boolean;
}

export default function ThemeToggle({ collapsed = false }: ThemeToggleProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center gap-3 px-3 py-2.5 rounded-full">
        <div className="w-5 h-5" />
      </div>
    );
  }

  const isDark = resolvedTheme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="flex items-center gap-3 px-3 py-2.5 rounded-full w-full text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#3c3c3c] transition-all duration-200"
    >
      {isDark ? (
        <Sun className="w-5 h-5 flex-shrink-0" />
      ) : (
        <Moon className="w-5 h-5 flex-shrink-0" />
      )}
      {!collapsed && (
        <span className="text-sm font-medium">
          {isDark ? "Light mode" : "Dark mode"}
        </span>
      )}
    </button>
  );
}
