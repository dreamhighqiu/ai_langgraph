/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

"use client";
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFKc2RnPT06YWUyZjkxNmE=

import * as React from "react";
import {
  Search,
  Plus,
  MoreVertical,
  Pencil,
  Trash2,
  Copy,
  FileText,
  ChevronLeft,
  ChevronRight,
  GripVertical,
  Filter,
  Sparkles,
  Upload,
  Download,
  ClipboardList,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import type { TestCaseInfo, Priority, TestCaseState, TestCaseTemplate } from "@/lib/api/types";
import {
  DndContext,
  DragOverlay,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  useSortable,
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
// NOTE  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFKc2RnPT06YWUyZjkxNmE=

interface TestCaseListProps {
  testCases: TestCaseInfo[];
  loading: boolean;
  selectedIds: Set<string>;
  onSelectIds: (ids: Set<string>) => void;
  onSearch: (query: string) => void;
  onFilterPriority: (priority: string) => void;
  onFilterStatus: (status: string) => void;
  onCreateTestCase: () => void;
  onEditTestCase: (testCase: TestCaseInfo) => void;
  onDeleteTestCase: (testCase: TestCaseInfo) => void;
  onBulkDelete?: () => void;
  onViewTestCase: (testCase: TestCaseInfo) => void;
  onQuickCreateTestCase?: (title: string, template: TestCaseTemplate) => void;
  onAIGenerate?: () => void;
  onAIGenerateFromDocument?: () => void;
  onOpenAIChat?: () => void;
  aiChatOpen?: boolean;
  folderName?: string;
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    onPageChange: (page: number) => void;
  };
}

const priorityColors: Record<Priority, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-green-500",
};

const priorityLabels: Record<Priority, string> = {
  critical: "紧急",
  high: "高",
  medium: "中",
  low: "低",
};
// @ts-expect-error  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFKc2RnPT06YWUyZjkxNmE=

const statusLabels: Record<TestCaseState, string> = {
  active: "激活",
  draft: "草稿",
  deprecated: "废弃",
};
// @ts-expect-error  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFKc2RnPT06YWUyZjkxNmE=

export function TestCaseList({
  testCases,
  loading,
  selectedIds,
  onSelectIds,
  onSearch,
  onFilterPriority,
  onFilterStatus,
  onCreateTestCase,
  onEditTestCase,
  onDeleteTestCase,
  onBulkDelete,
  onViewTestCase,
  onQuickCreateTestCase,
  onAIGenerate,
  onAIGenerateFromDocument,
  onOpenAIChat,
  aiChatOpen,
  folderName,
  pagination,
}: TestCaseListProps) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [quickCreateTitle, setQuickCreateTitle] = React.useState("");
  const [quickCreateTemplate, setQuickCreateTemplate] = React.useState<TestCaseTemplate>("test_case");
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [localTestCases, setLocalTestCases] = React.useState<TestCaseInfo[]>(testCases);

  // 同步外部testCases到本地状态
  React.useEffect(() => {
    setLocalTestCases(testCases);
  }, [testCases]);

  // 配置拖动传感器
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 移动8px后才开始拖动
      },
    })
  );

  // 拖动开始
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  // 拖动结束
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || active.id === over.id) {
      return;
    }

    setLocalTestCases((items) => {
      const oldIndex = items.findIndex((item) => item.id === active.id);
      const newIndex = items.findIndex((item) => item.id === over.id);
      const newItems = arrayMove(items, oldIndex, newIndex);

      // 这里可以调用API保存新的顺序
      toast.success("测试用例顺序已更新");

      return newItems;
    });
  };

  // 全选/取消全选
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectIds(new Set(localTestCases.map((tc) => tc.id)));
    } else {
      onSelectIds(new Set());
    }
  };

  // 单选
  const handleSelect = (id: string, checked: boolean) => {
    const newIds = new Set(selectedIds);
    if (checked) {
      newIds.add(id);
    } else {
      newIds.delete(id);
    }
    onSelectIds(newIds);
  };

  // 搜索
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  // 快速创建
  const handleQuickCreate = () => {
    if (!quickCreateTitle.trim()) {
      toast.error("请输入测试用例标题");
      return;
    }
    onQuickCreateTestCase?.(quickCreateTitle.trim(), quickCreateTemplate);
    setQuickCreateTitle("");
  };

  const isAllSelected =
    localTestCases.length > 0 && selectedIds.size === localTestCases.length;
  const isPartialSelected =
    selectedIds.size > 0 && selectedIds.size < localTestCases.length;

  // 可拖动的测试用例行组件
  const DraggableTestCaseRow = ({ testCase }: { testCase: TestCaseInfo }) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      transition,
      isDragging,
    } = useSortable({ id: testCase.id });

    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
      opacity: isDragging ? 0.5 : 1,
    };

    return (
      <tr
        ref={setNodeRef}
        style={style}
        className={cn(
          "group border-b hover:bg-muted/50 transition-colors",
          selectedIds.has(testCase.id) && "bg-muted/30"
        )}
      >
        <td className="p-3">
          <div className="flex items-center gap-1">
            <div
              {...attributes}
              {...listeners}
              className="cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100"
            >
              <GripVertical className="h-4 w-4 text-muted-foreground" />
            </div>
            <Checkbox
              checked={selectedIds.has(testCase.id)}
              onCheckedChange={(checked) =>
                handleSelect(testCase.id, checked as boolean)
              }
              aria-label={`选择 ${testCase.name}`}
            />
          </div>
        </td>
        <td className="p-3 overflow-hidden">
          <span className="text-sm text-muted-foreground truncate block">
            {testCase.identifier}
          </span>
        </td>
        <td className="p-3 overflow-hidden">
          <button
            onClick={() => onViewTestCase(testCase)}
            className="truncate text-left text-sm font-medium hover:text-primary block w-full"
          >
            {testCase.name}
          </button>
        </td>
        <td className="p-3 overflow-hidden">
          <Badge
            variant={
              testCase.priority === "critical"
                ? "destructive"
                : testCase.priority === "high"
                ? "default"
                : "secondary"
            }
            className="truncate"
          >
            {priorityLabels[testCase.priority]}
          </Badge>
        </td>
        <td className="p-3 overflow-hidden">
          <span className="text-sm truncate block">
            {testCase.owner || testCase.created_by || "-"}
          </span>
        </td>
        <td className="p-3 overflow-hidden">
          <div className="flex flex-wrap gap-1">
            {testCase.tags && testCase.tags.length > 0 ? (
              testCase.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs truncate">
                  {tag}
                </Badge>
              ))
            ) : (
              <span className="text-sm text-muted-foreground">-</span>
            )}
            {testCase.tags && testCase.tags.length > 2 && (
              <Badge variant="outline" className="text-xs">
                +{testCase.tags.length - 2}
              </Badge>
            )}
          </div>
        </td>
        <td className="p-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 opacity-0 group-hover:opacity-100"
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onViewTestCase(testCase)}>
                <FileText className="mr-2 h-4 w-4" />
                查看详情
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onEditTestCase(testCase)}>
                <Pencil className="mr-2 h-4 w-4" />
                编辑
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="mr-2 h-4 w-4" />
                复制
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onClick={() => onDeleteTestCase(testCase)}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                删除
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </td>
      </tr>
    );
  };

  return (
    <div className="flex h-full flex-col">
      {/* 顶部标题栏 */}
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">{folderName || "全部用例"}</h2>
          <span className="text-sm text-muted-foreground">
            ({pagination?.total || testCases.length})
          </span>
        </div>
        <div className="flex items-center gap-2">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="搜索用例..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-48 pl-9"
            />
          </form>
          <Button variant="outline" size="sm">
            <Filter className="mr-2 h-4 w-4" />
            筛选
          </Button>
          {onAIGenerate && (
            <Button variant="outline" size="sm" onClick={onAIGenerate}>
              <Sparkles className="mr-2 h-4 w-4" />
              AI 生成
            </Button>
          )}
          {onAIGenerateFromDocument && (
            <Button variant="outline" size="sm" onClick={onAIGenerateFromDocument}>
              <Upload className="mr-2 h-4 w-4" />
              从文档生成
            </Button>
          )}
          <Button onClick={onCreateTestCase}>
            <Plus className="mr-2 h-4 w-4" />
            新建用例
          </Button>
          {onOpenAIChat && !aiChatOpen && (
            <Button variant="outline" size="sm" onClick={onOpenAIChat}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              展开 AI 助手
            </Button>
          )}
        </div>
      </div>

      {/* 批量操作栏 */}
      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 border-b bg-muted/50 px-4 py-2">
          <span className="text-sm text-muted-foreground">
            已选择 {selectedIds.size} 项
          </span>
          <Button variant="outline" size="sm">
            批量编辑
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
            onClick={onBulkDelete}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            批量删除
          </Button>
        </div>
      )}

      {/* 列表 */}
      <ScrollArea className="flex-1">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="text-muted-foreground">加载中...</div>
          </div>
        ) : testCases.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-6 py-16">
            {/* 图标 */}
            <div className="flex h-16 w-16 items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/30">
              <ClipboardList className="h-8 w-8 text-muted-foreground/50" />
            </div>

            {/* 标题和描述 */}
            <div className="text-center">
              <h3 className="text-lg font-semibold">添加测试用例</h3>
              <p className="text-sm text-muted-foreground">
                您可以通过以下方式创建测试用例
              </p>
            </div>

            {/* 快速创建输入框 */}
            {onQuickCreateTestCase && (
              <div className="flex w-full max-w-xl items-center gap-2 px-4">
                <Select
                  value={quickCreateTemplate}
                  onValueChange={(value) => setQuickCreateTemplate(value as TestCaseTemplate)}
                >
                  <SelectTrigger className="w-28">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="test_case">Manual</SelectItem>
                    <SelectItem value="bdd">AI BDD</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  placeholder="Enter test case title"
                  value={quickCreateTitle}
                  onChange={(e) => setQuickCreateTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleQuickCreate();
                    }
                  }}
                  className="flex-1"
                />
                <Button onClick={handleQuickCreate}>Create</Button>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex items-center gap-3">
              {onAIGenerate && (
                <Button variant="outline" onClick={onAIGenerate}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate with AI
                </Button>
              )}
              {onAIGenerateFromDocument && (
                <Button variant="outline" onClick={onAIGenerateFromDocument}>
                  <Upload className="mr-2 h-4 w-4" />
                  Generate from Document
                </Button>
              )}
              <Button variant="outline" onClick={() => toast.info("导入测试用例功能开发中")}>
                <Download className="mr-2 h-4 w-4" />
                Import Test Cases
              </Button>
            </div>
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <table className="w-full table-fixed">
              <thead className="sticky top-0 bg-card">
                <tr className="border-b text-left text-xs font-medium uppercase text-muted-foreground">
                  <th className="w-16 p-3">
                    <Checkbox
                      checked={isAllSelected}
                      onCheckedChange={handleSelectAll}
                      aria-label="全选"
                    />
                  </th>
                  <th className="w-28 p-3">ID</th>
                  <th className="p-3">TITLE</th>
                  <th className="w-28 p-3">PRIORITY</th>
                  <th className="w-36 p-3">OWNER</th>
                  <th className="w-44 p-3">TAGS</th>
                  <th className="w-16 p-3"></th>
                </tr>
              </thead>
              <SortableContext
                items={localTestCases.map((tc) => tc.id)}
                strategy={verticalListSortingStrategy}
              >
                <tbody>
                  {localTestCases.map((testCase) => (
                    <DraggableTestCaseRow key={testCase.id} testCase={testCase} />
                  ))}
                </tbody>
              </SortableContext>
            </table>

            {/* 拖动覆盖层 */}
            <DragOverlay>
              {activeId ? (
                <div className="rounded-md bg-accent p-3 shadow-lg">
                  <span className="text-sm font-medium">
                    {localTestCases.find((tc) => tc.id === activeId)?.name}
                  </span>
                </div>
              ) : null}
            </DragOverlay>
          </DndContext>
        )}
      </ScrollArea>

      {/* 分页 */}
      {pagination && pagination.total > pagination.pageSize && (
        <div className="flex items-center justify-between border-t px-4 py-3">
          <div className="text-sm text-muted-foreground">
            显示 {(pagination.page - 1) * pagination.pageSize + 1} -{" "}
            {Math.min(pagination.page * pagination.pageSize, pagination.total)}{" "}
            / {pagination.total} 条
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.page === 1}
              onClick={() => pagination.onPageChange(pagination.page - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              上一页
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={
                pagination.page >=
                Math.ceil(pagination.total / pagination.pageSize)
              }
              onClick={() => pagination.onPageChange(pagination.page + 1)}
            >
              下一页
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* 快速创建 */}
      {onQuickCreateTestCase && (
        <div className="flex items-center gap-2 border-t bg-muted/30 px-4 py-3">
          <Select
            value={quickCreateTemplate}
            onValueChange={(value) => setQuickCreateTemplate(value as TestCaseTemplate)}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="test_case">Manual</SelectItem>
              <SelectItem value="test_case_bdd">AI BDD</SelectItem>
            </SelectContent>
          </Select>
          <Input
            placeholder="Enter test case title"
            value={quickCreateTitle}
            onChange={(e) => setQuickCreateTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleQuickCreate();
              }
            }}
            className="flex-1"
          />
          <Button onClick={handleQuickCreate}>Create</Button>
        </div>
      )}
    </div>
  );
}

