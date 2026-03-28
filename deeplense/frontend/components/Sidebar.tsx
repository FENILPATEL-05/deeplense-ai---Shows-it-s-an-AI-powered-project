"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Search,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import ThemeToggle from "./ThemeToggle";

const navItems = [
  { href: "/search", label: "Search", icon: Search },
  { href: "/collection", label: "Collection", icon: FolderOpen },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [autoCollapsed, setAutoCollapsed] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setAutoCollapsed(true);
      } else {
        setAutoCollapsed(false);
      }
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const isCollapsed = collapsed || autoCollapsed;

  return (
    <aside
      className={`flex-shrink-0 flex flex-col h-full border-r border-[#e8eaed] dark:border-[#3c3c3c] bg-[#f8f9fa] dark:bg-[#2d2d2d] transition-all duration-200 ${
        isCollapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 flex-shrink-0">
        <div className="w-8 h-8 flex-shrink-0">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle
              cx="16"
              cy="16"
              r="14"
              stroke="currentColor"
              strokeWidth="2"
              className="text-accent-light dark:text-accent-dark"
            />
            <circle
              cx="16"
              cy="16"
              r="6"
              stroke="currentColor"
              strokeWidth="2"
              className="text-accent-light dark:text-accent-dark"
            />
            <circle
              cx="16"
              cy="16"
              r="2"
              fill="currentColor"
              className="text-accent-light dark:text-accent-dark"
            />
            <line
              x1="16"
              y1="2"
              x2="16"
              y2="10"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-accent-light dark:text-accent-dark"
            />
            <line
              x1="16"
              y1="22"
              x2="16"
              y2="30"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-accent-light dark:text-accent-dark"
            />
            <line
              x1="2"
              y1="16"
              x2="10"
              y2="16"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-accent-light dark:text-accent-dark"
            />
            <line
              x1="22"
              y1="16"
              x2="30"
              y2="16"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-accent-light dark:text-accent-dark"
            />
          </svg>
        </div>
        {!isCollapsed && (
          <span className="text-lg font-semibold text-[#202124] dark:text-[#e8eaed] truncate">
            Deeplense
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-full transition-all duration-200 ${
                isActive
                  ? "bg-[#1a73e8]/10 dark:bg-[#8ab4f8]/10 text-[#1a73e8] dark:text-[#8ab4f8]"
                  : "text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#3c3c3c]"
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && (
                <span className="text-sm font-medium truncate">{label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom: Theme + Collapse */}
      <div className="px-2 py-4 space-y-1 border-t border-[#e8eaed] dark:border-[#3c3c3c]">
        <ThemeToggle collapsed={isCollapsed} />
        {!autoCollapsed && (
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-full w-full text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8eaed] dark:hover:bg-[#3c3c3c] transition-all duration-200"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5 flex-shrink-0" />
            ) : (
              <ChevronLeft className="w-5 h-5 flex-shrink-0" />
            )}
            {!isCollapsed && (
              <span className="text-sm font-medium">Collapse</span>
            )}
          </button>
        )}
      </div>
    </aside>
  );
}
