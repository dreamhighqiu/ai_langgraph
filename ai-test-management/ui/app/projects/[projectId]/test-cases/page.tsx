
// TODO  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0hOdk1RPT06ZDhhN2JkZGY=

"use client";
// eslint-disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0hOdk1RPT06ZDhhN2JkZGY=

import * as React from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { MainLayout } from "@/components/layout";
import {
  FolderTree,
  TestCaseList,
  TestCaseDialog,
  MoveFolderDialog,
  AIGenerateDialog,
  AIGenerateFromDocumentDialog,
} from "@/components/test-cases";
import type { FolderTreeRef } from "@/components/test-cases";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { AIChatContainer } from "@/components/langgraph/AIChatContainer";
import { ClientProvider } from "@/providers/ClientProvider";
import { Assistant } from "@langchain/langgraph-sdk";
import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  getTestCases,
  getFolderTestCases,
  createTestCase,
  updateTestCase,
  deleteTestCase,
  bulkDeleteTestCases,
} from "@/lib/api/testCases";
import {
  createFolder,
  updateFolder,
  deleteFolder,
} from "@/lib/api/folders";
import type {
  TestCaseInfo,
  TestCaseCreate,
  FolderInfo,
  FolderCreate,
} from "@/lib/api/types";
// eslint-disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0hOdk1RPT06ZDhhN2JkZGY=

export default function TestCasesPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  // 文件夹树 ref
  const folderTreeRef = React.useRef<FolderTreeRef>(null);

  // 状态
  const [testCases, setTestCases] = React.useState<TestCaseInfo[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [selectedFolderId, setSelectedFolderId] = React.useState<string | null>(
    null
  );
  const [selectedIds, setSelectedIds] = React.useState<Set<string>>(new Set());

  // 分页
  const [page, setPage] = React.useState(1);
  const [pageSize] = React.useState(20);
  const [total, setTotal] = React.useState(0);

  // 筛选
  const [searchQuery, setSearchQuery] = React.useState("");
  const [priorityFilter, setPriorityFilter] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("");

  // 测试用例对话框
  const [testCaseDialogOpen, setTestCaseDialogOpen] = React.useState(false);
  const [editingTestCase, setEditingTestCase] =
    React.useState<TestCaseInfo | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  // 删除确认对话框
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [deletingTestCase, setDeletingTestCase] =
    React.useState<TestCaseInfo | null>(null);

  // 批量删除确认对话框
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = React.useState(false);

  // 文件夹对话框
  const [folderDialogOpen, setFolderDialogOpen] = React.useState(false);
  const [editingFolder, setEditingFolder] = React.useState<FolderInfo | null>(
    null
  );
  const [folderParentId, setFolderParentId] = React.useState<string | undefined>();
  const [folderFormData, setFolderFormData] = React.useState<FolderCreate>({
    name: "",
    description: "",
  });

  // 删除文件夹对话框
  const [deleteFolderDialogOpen, setDeleteFolderDialogOpen] =
    React.useState(false);
  const [deletingFolder, setDeletingFolder] = React.useState<FolderInfo | null>(
    null
  );

  // 创建测试用例时指定的文件夹
  const [createTestCaseFolder, setCreateTestCaseFolder] = React.useState<FolderInfo | null>(null);

  // 当前选中的文件夹名称
  const [selectedFolderName, setSelectedFolderName] = React.useState<string | undefined>();

  // 加载测试用例
  const loadTestCases = React.useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        p: page,
        page_size: pageSize,
        search: searchQuery || undefined,
        priority: priorityFilter && priorityFilter !== "all" ? priorityFilter : undefined,
        status: statusFilter && statusFilter !== "all" ? statusFilter : undefined,
      };

      let response;
      if (selectedFolderId) {
        response = await getFolderTestCases(projectId, selectedFolderId, params);
      } else {
        response = await getTestCases(projectId, params);
      }

      if (response.success) {
        setTestCases(response.data || response.test_cases || []);
        setTotal(response.info?.total || 0);
      }
    } catch (error) {
      console.error("Failed to load test cases:", error);
      toast.error("加载测试用例失败");
    } finally {
      setLoading(false);
    }
  }, [projectId, selectedFolderId, page, pageSize, searchQuery, priorityFilter, statusFilter]);

  React.useEffect(() => {
    if (projectId) {
      loadTestCases();
    }
  }, [projectId, loadTestCases]);

  // 选择文件夹
  const handleSelectFolder = (folder: FolderInfo | null) => {
    setSelectedFolderId(folder?.id || null);
    setSelectedFolderName(folder?.name);
    setPage(1);
    setSelectedIds(new Set());
  };

  // 创建/编辑测试用例
  const handleSubmitTestCase = async (data: TestCaseCreate) => {
    try {
      setSubmitting(true);
      if (editingTestCase) {
        await updateTestCase(projectId, editingTestCase.id, data);
        toast.success("测试用例更新成功");
      } else {
        // 优先使用从文件夹菜单指定的文件夹
        const targetFolderId = createTestCaseFolder?.id || selectedFolderId;
        await createTestCase(projectId, targetFolderId, data);
        toast.success("测试用例创建成功");
      }
      setTestCaseDialogOpen(false);
      setEditingTestCase(null);
      setCreateTestCaseFolder(null);
      loadTestCases();
      // 刷新文件夹树以更新用例计数（测试用例操作需要刷新计数）
      folderTreeRef.current?.refresh();
    } catch (error) {
      console.error("Failed to save test case:", error);
      toast.error(editingTestCase ? "更新测试用例失败" : "创建测试用例失败");
    } finally {
      setSubmitting(false);
    }
  };

  // 从文件夹菜单创建测试用例
  const handleCreateTestCaseInFolder = (folder: FolderInfo) => {
    setCreateTestCaseFolder(folder);
    setEditingTestCase(null);
    setTestCaseDialogOpen(true);
  };

  // 批量删除测试用例
  const handleBulkDelete = () => {
    if (selectedIds.size === 0) {
      toast.error("请先选择要删除的测试用例");
      return;
    }
    setBulkDeleteDialogOpen(true);
  };

  const confirmBulkDelete = async () => {
    try {
      const idsArray = Array.from(selectedIds);
      const response = await bulkDeleteTestCases(projectId, idsArray);

      if (response.success) {
        toast.success(response.message || `成功删除 ${response.affected_count} 个测试用例`);
        setSelectedIds(new Set());
        setBulkDeleteDialogOpen(false);
        loadTestCases();
        folderTreeRef.current?.refresh();
      } else {
        toast.error("批量删除失败");
      }
    } catch (error) {
      console.error("Failed to bulk delete test cases:", error);
      toast.error("批量删除失败，请稍后重试");
    }
  };

  // 移动文件夹状态
  const [moveFolderDialogOpen, setMoveFolderDialogOpen] = React.useState(false);
  const [movingFolder, setMovingFolder] = React.useState<FolderInfo | null>(null);

  // AI生成对话框状态
  const [aiGenerateDialogOpen, setAiGenerateDialogOpen] = React.useState(false);
  const [aiGenerateFromDocDialogOpen, setAiGenerateFromDocDialogOpen] = React.useState(false);

  // AI聊天面板状态
  const [aiChatOpen, setAiChatOpen] = React.useState(false);
  const [aiChatInitialPrompt, setAiChatInitialPrompt] = React.useState<string>("");
  const [aiChatKey, setAiChatKey] = React.useState<number>(0);
  const [assistant, setAssistant] = React.useState<Assistant | null>(null);

  // 初始化 Assistant
  React.useEffect(() => {
    const initAssistant = async () => {
      try {
        const assistantId = "testcase_generator_agent";
        const mockAssistant: Assistant = {
          assistant_id: assistantId,
          graph_id: assistantId,
          config: {
            configurable: {
              // 添加上下文信息，供智能体使用
              project_identifier: projectId,
              folder_id: selectedFolderId || "",
              template_type: "test_case", // 默认使用普通测试用例模板
            }
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          metadata: {},
          version: 1,
          name: "测试用例生成助手",
          context: {},
        };
        setAssistant(mockAssistant);
      } catch (error) {
        console.error("Failed to initialize assistant:", error);
      }
    };
    initAssistant();
  }, [projectId, selectedFolderId]); // 当 projectId 或 selectedFolderId 变化时重新初始化

  // 移动文件夹
  const handleMoveFolder = (folder: FolderInfo) => {
    setMovingFolder(folder);
    setMoveFolderDialogOpen(true);
  };

  // AI生成成功回调
  const handleAIGenerateSuccess = (testCases: TestCaseInfo[]) => {
    toast.success(`成功生成 ${testCases.length} 个测试用例`);
    loadTestCases();
    folderTreeRef.current?.refresh();
  };

  // 从对话框打开AI聊天面板
  const handleOpenAIChatFromDialog = (prompt: string) => {
    // 设置初始提示词并更新 key 以创建新对话
    setAiChatInitialPrompt(prompt);
    setAiChatKey(prev => prev + 1); // 更新 key 强制重新挂载，创建新对话

    setAiChatOpen(true);
    // 关闭生成对话框
    setAiGenerateDialogOpen(false);
    setAiGenerateFromDocDialogOpen(false);
  };

  // 移动文件夹成功回调 - 本地更新树
  const handleMoveFolderSuccess = (folderId: string, newParentId: string | null, updatedFolder: FolderInfo) => {
    folderTreeRef.current?.moveFolderLocally(folderId, newParentId, updatedFolder);
  };

  // 快速创建测试用例
  const handleQuickCreateTestCase = async (title: string, template: "test_case" | "test_case_bdd") => {
    try {
      const data: TestCaseCreate = {
        name: title,
        priority: "medium",
        case_type: "functional",
        template,
      };
      await createTestCase(projectId, selectedFolderId || null, data);
      toast.success("测试用例创建成功");
      loadTestCases();
      folderTreeRef.current?.refresh();
    } catch (error) {
      console.error("Failed to create test case:", error);
      toast.error("创建测试用例失败");
    }
  };

  // 删除测试用例
  const handleDeleteTestCase = async () => {
    if (!deletingTestCase) return;
    try {
      setSubmitting(true);
      await deleteTestCase(projectId, deletingTestCase.id);
      toast.success("测试用例删除成功");
      setDeleteDialogOpen(false);
      setDeletingTestCase(null);
      loadTestCases();
      // 刷新文件夹树以更新用例计数
      folderTreeRef.current?.refresh();
    } catch (error) {
      console.error("Failed to delete test case:", error);
      toast.error("删除测试用例失败");
    } finally {
      setSubmitting(false);
    }
  };

  // 创建文件夹
  const handleCreateFolder = (parentId?: string) => {
    setEditingFolder(null);
    setFolderParentId(parentId);
    setFolderFormData({ name: "", description: "" });
    setFolderDialogOpen(true);
  };

  // 编辑文件夹
  const handleEditFolder = (folder: FolderInfo) => {
    setEditingFolder(folder);
    setFolderParentId(undefined);
    setFolderFormData({
      name: folder.name,
      description: folder.description || "",
    });
    setFolderDialogOpen(true);
  };

  // 提交文件夹
  const handleSubmitFolder = async () => {
    if (!folderFormData.name.trim()) {
      toast.error("请输入文件夹名称");
      return;
    }
    try {
      setSubmitting(true);
      if (editingFolder) {
        // 编辑文件夹 - 使用本地更新
        const response = await updateFolder(projectId, editingFolder.id, folderFormData);
        toast.success("文件夹更新成功");
        setFolderDialogOpen(false);
        // 本地更新文件夹
        if (response.success && response.data) {
          folderTreeRef.current?.updateFolderLocally(editingFolder.id, response.data);
        }
      } else {
        // 创建文件夹 - 使用本地添加
        const response = await createFolder(projectId, {
          ...folderFormData,
          parent_id: folderParentId,
        });
        toast.success("文件夹创建成功");
        setFolderDialogOpen(false);
        // 本地添加文件夹
        if (response.success && response.data) {
          folderTreeRef.current?.addFolderLocally(response.data, folderParentId || null);
        }
      }
    } catch (error) {
      console.error("Failed to save folder:", error);
      toast.error(editingFolder ? "更新文件夹失败" : "创建文件夹失败");
    } finally {
      setSubmitting(false);
    }
  };

  // 删除文件夹
  const handleDeleteFolder = async () => {
    if (!deletingFolder) return;
    try {
      setSubmitting(true);
      await deleteFolder(projectId, deletingFolder.id);
      toast.success("文件夹删除成功");
      setDeleteFolderDialogOpen(false);
      // 本地删除文件夹
      folderTreeRef.current?.removeFolderLocally(deletingFolder.id);
      if (selectedFolderId === deletingFolder.id) {
        setSelectedFolderId(null);
      }
      setDeletingFolder(null);
    } catch (error) {
      console.error("Failed to delete folder:", error);
      toast.error("删除文件夹失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <MainLayout title="测试用例">
      <div className="relative flex h-[calc(100vh-8rem)] rounded-lg border bg-card overflow-hidden">
        <div className="flex h-full w-full">
          {/* 文件夹树 */}
          <div className="w-80 shrink-0">
            <FolderTree
              ref={folderTreeRef}
              projectId={projectId}
              selectedFolderId={selectedFolderId}
              onSelectFolder={handleSelectFolder}
              onCreateFolder={handleCreateFolder}
              onEditFolder={handleEditFolder}
              onDeleteFolder={(folder) => {
                setDeletingFolder(folder);
                setDeleteFolderDialogOpen(true);
              }}
              onCreateTestCase={handleCreateTestCaseInFolder}
              onMoveFolder={handleMoveFolder}
            />
          </div>

          {/* 测试用例列表 */}
          <div className="flex-1">
            <TestCaseList
              testCases={testCases}
              loading={loading}
              selectedIds={selectedIds}
              onSelectIds={setSelectedIds}
              onSearch={setSearchQuery}
              onFilterPriority={setPriorityFilter}
              onFilterStatus={setStatusFilter}
              onCreateTestCase={() => {
                setEditingTestCase(null);
                setTestCaseDialogOpen(true);
              }}
              onEditTestCase={(tc) => {
                setEditingTestCase(tc);
                setTestCaseDialogOpen(true);
              }}
              onDeleteTestCase={(tc) => {
                setDeletingTestCase(tc);
                setDeleteDialogOpen(true);
              }}
              onBulkDelete={handleBulkDelete}
              onViewTestCase={(tc) => {
                setEditingTestCase(tc);
                setTestCaseDialogOpen(true);
              }}
              onQuickCreateTestCase={handleQuickCreateTestCase}
              onAIGenerate={() => setAiGenerateDialogOpen(true)}
              onAIGenerateFromDocument={() => setAiGenerateFromDocDialogOpen(true)}
              onOpenAIChat={() => setAiChatOpen(true)}
              aiChatOpen={aiChatOpen}
              folderName={selectedFolderName}
              pagination={{
                page,
                pageSize,
                total,
                onPageChange: setPage,
              }}
            />
          </div>
        </div>

        {/* 右侧悬浮 AI 聊天面板 */}
        {assistant && (
          <div
            key={aiChatKey}
            className={cn(
              "absolute right-0 top-0 z-50 h-full w-[1200px] bg-background transition-transform duration-300 ease-in-out",
              aiChatOpen ? "translate-x-0 border-l shadow-2xl" : "translate-x-full"
            )}
          >
            <ClientProvider
              deploymentUrl={process.env.NEXT_PUBLIC_LANGGRAPH_API_URL || "http://localhost:2026"}
              apiKey={process.env.NEXT_PUBLIC_LANGSMITH_API_KEY || ""}
            >
              <AIChatContainer
                assistant={assistant}
                initialPrompt={aiChatInitialPrompt}
                onClose={() => setAiChatOpen(false)}
                createNewThread={aiChatKey > 0}
                onTestCaseCreated={() => {
                  // AI 生成测试用例后自动刷新列表
                  loadTestCases();
                  folderTreeRef.current?.refresh();
                }}
              />
            </ClientProvider>
          </div>
        )}
      </div>

      {/* 测试用例对话框 */}
      <TestCaseDialog
        open={testCaseDialogOpen}
        onOpenChange={setTestCaseDialogOpen}
        testCase={editingTestCase}
        onSubmit={handleSubmitTestCase}
        submitting={submitting}
        folderName={createTestCaseFolder?.name || selectedFolderName}
        projectId={projectId}
      />

      {/* 删除测试用例确认 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>删除测试用例</DialogTitle>
            <DialogDescription>
              确定要删除测试用例 "{deletingTestCase?.name}" 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteTestCase}
              disabled={submitting}
            >
              {submitting ? "删除中..." : "删除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 文件夹对话框 */}
      <Dialog open={folderDialogOpen} onOpenChange={setFolderDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingFolder ? "编辑文件夹" : "新建文件夹"}
            </DialogTitle>
            <DialogDescription>
              {editingFolder ? "修改文件夹信息" : "创建一个新的文件夹"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="folder-name">文件夹名称</Label>
              <Input
                id="folder-name"
                value={folderFormData.name}
                onChange={(e) =>
                  setFolderFormData({ ...folderFormData, name: e.target.value })
                }
                placeholder="请输入文件夹名称"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="folder-description">描述</Label>
              <Textarea
                id="folder-description"
                value={folderFormData.description}
                onChange={(e) =>
                  setFolderFormData({
                    ...folderFormData,
                    description: e.target.value,
                  })
                }
                placeholder="请输入描述（可选）"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFolderDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmitFolder} disabled={submitting}>
              {submitting ? "保存中..." : editingFolder ? "保存" : "创建"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除文件夹确认 */}
      <Dialog
        open={deleteFolderDialogOpen}
        onOpenChange={setDeleteFolderDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>删除文件夹</DialogTitle>
            <DialogDescription>
              确定要删除文件夹 "{deletingFolder?.name}" 吗？文件夹内的所有内容也将被删除，此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteFolderDialogOpen(false)}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteFolder}
              disabled={submitting}
            >
              {submitting ? "删除中..." : "删除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 批量删除确认对话框 */}
      <Dialog
        open={bulkDeleteDialogOpen}
        onOpenChange={setBulkDeleteDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>批量删除测试用例</DialogTitle>
            <DialogDescription>
              确定要删除选中的 {selectedIds.size} 个测试用例吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setBulkDeleteDialogOpen(false)}
            >
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={confirmBulkDelete}
            >
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 移动文件夹对话框 */}
      <MoveFolderDialog
        open={moveFolderDialogOpen}
        onOpenChange={setMoveFolderDialogOpen}
        projectId={projectId}
        folder={movingFolder}
        onMoveSuccess={handleMoveFolderSuccess}
      />

      {/* AI生成测试用例对话框 */}
      <AIGenerateDialog
        open={aiGenerateDialogOpen}
        onOpenChange={setAiGenerateDialogOpen}
        projectId={projectId}
        folderId={selectedFolderId}
        onSuccess={handleAIGenerateSuccess}
        onOpenChat={handleOpenAIChatFromDialog}
      />

      {/* AI从文档生成测试用例对话框 */}
      <AIGenerateFromDocumentDialog
        open={aiGenerateFromDocDialogOpen}
        onOpenChange={setAiGenerateFromDocDialogOpen}
        projectId={projectId}
        folderId={selectedFolderId}
        onSuccess={handleAIGenerateSuccess}
        onOpenChat={handleOpenAIChatFromDialog}
      />
    </MainLayout>
  );
}
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0hOdk1RPT06ZDhhN2JkZGY=

