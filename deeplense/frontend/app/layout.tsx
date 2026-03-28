import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "next-themes";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Deeplense — Image Search",
  description: "AI-powered image search platform using CLIP embeddings",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex h-screen overflow-hidden bg-white dark:bg-[#1f1f1f]">
            <Sidebar />
            <main className="flex-1 overflow-auto">{children}</main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
