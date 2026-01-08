

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlU1MGFRPT06N2QzOWZhMTM=

export const metadata: Metadata = {
  title: "但问智能测试管理平台",
  description: "AI 驱动的测试管理系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <NuqsAdapter>{children}</NuqsAdapter>
        <Toaster />
      </body>
    </html>
  );
}
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlU1MGFRPT06N2QzOWZhMTM=

