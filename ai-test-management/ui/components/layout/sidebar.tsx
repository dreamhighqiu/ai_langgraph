/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkRkaFZnPT06YjE4ZmQ5NTQ=

"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FolderKanban,
  FileText,
  PlayCircle,
  ClipboardList,
  BarChart3,
  ChevronDown,
  Settings,
  Home,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ProjectInfo } from "@/lib/api/types";
// FIXME  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkRkaFZnPT06YjE4ZmQ5NTQ=

interface SidebarProps {
  projects: ProjectInfo[];
  currentProject?: ProjectInfo | null;
  onProjectChange?: (project: ProjectInfo) => void;
}

const navItems = [
  {
    title: "测试用例",
    href: "/test-cases",
    icon: FileText,
  },
  {
    title: "测试运行",
    href: "/test-runs",
    icon: PlayCircle,
  },
  {
    title: "测试计划",
    href: "/test-plans",
    icon: ClipboardList,
  },
  {
    title: "报告",
    href: "/reports",
    icon: BarChart3,
  },
];
// FIXME  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkRkaFZnPT06YjE4ZmQ5NTQ=

export function Sidebar({
  projects,
  currentProject,
  onProjectChange,
}: SidebarProps) {
  const pathname = usePathname();

  const getNavHref = (baseHref: string) => {
    if (!currentProject) return "#";
    return `/projects/${currentProject.identifier}${baseHref}`;
  };

  const isActive = (href: string) => {
    if (!currentProject) return false;
    const fullHref = getNavHref(href);
    return pathname.startsWith(fullHref);
  };

  return (
    <div className="flex h-full w-60 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/projects" className="flex items-center gap-2">
          <FolderKanban className="h-6 w-6 text-primary" />
          <span className="font-semibold">智能测试管理平台</span>
        </Link>
      </div>

      {/* Project Selector */}
      <div className="border-b p-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              className="w-full justify-between"
              disabled={projects.length === 0}
            >
              <span className="truncate">
                {currentProject?.name || "选择项目"}
              </span>
              <ChevronDown className="h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-52">
            {projects.map((project) => (
              <DropdownMenuItem
                key={project.identifier}
                onClick={() => onProjectChange?.(project)}
                className={cn(
                  currentProject?.identifier === project.identifier &&
                    "bg-accent"
                )}
              >
                <span className="truncate">{project.name}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-2">
        <nav className="flex flex-col gap-1">
          <Link href="/projects">
            <Button
              variant={pathname === "/projects" ? "secondary" : "ghost"}
              className="w-full justify-start"
            >
              <Home className="mr-2 h-4 w-4" />
              所有项目
            </Button>
          </Link>

          {currentProject && (
            <>
              <div className="my-2 px-2 text-xs font-medium text-muted-foreground">
                项目导航
              </div>
              {navItems.map((item) => (
                <Link key={item.href} href={getNavHref(item.href)}>
                  <Button
                    variant={isActive(item.href) ? "secondary" : "ghost"}
                    className="w-full justify-start"
                  >
                    <item.icon className="mr-2 h-4 w-4" />
                    {item.title}
                  </Button>
                </Link>
              ))}
            </>
          )}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-3">
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="mr-2 h-4 w-4" />
          设置
        </Button>
      </div>
    </div>
  );
}
// NOTE  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VkRkaFZnPT06YjE4ZmQ5NTQ=

