"use client"

import * as React from "react"
import { useParams, useRouter } from "next/navigation"
import {
  Plus,
  Search,
  Download,
  FileText,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  Sparkles
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

import { RequirementAnalysisCreateDialog } from "@/components/requirement-analysis/create-dialog"
import { RequirementAnalysisEditDialog } from "@/components/requirement-analysis/edit-dialog"
import { AIChatContainer } from "@/components/langgraph/AIChatContainer"
import { ClientProvider } from "@/providers/ClientProvider"
import { Assistant } from "@langchain/langgraph-sdk"

interface RequirementAnalysis {
  id: string
  identifier: string
  title: string
  description: string | null
  status: string
  quality_score: number | null
  tags: string[]
  created_at: string
  updated_at: string
}

export default function RequirementAnalysisPage() {
  const params = useParams()
  const router = useRouter()
  
  const projectId = params.projectId as string
  
  const [requirementAnalyses, setRequirementAnalyses] = React.useState<RequirementAnalysis[]>([])
  const [loading, setLoading] = React.useState(true)
  const [searchTerm, setSearchTerm] = React.useState("")
  const [statusFilter, setStatusFilter] = React.useState<string>("all")
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [editDialogOpen, setEditDialogOpen] = React.useState(false)
  const [selectedRequirementAnalysis, setSelectedRequirementAnalysis] = React.useState<RequirementAnalysis | null>(null)
  
  // AI 聊天相关状态
  const [aiChatOpen, setAiChatOpen] = React.useState(false)
  const [aiChatInitialPrompt, setAiChatInitialPrompt] = React.useState("")
  const [aiChatKey, setAiChatKey] = React.useState(0)
  const [assistant, setAssistant] = React.useState<Assistant | null>(null)
  
  // 初始化 LangGraph Assistant
  React.useEffect(() => {
    const assistantId = process.env.NEXT_PUBLIC_REQUIREMENT_AGENT_ID || "requirement_analyzer_agent"
    setAssistant({
      assistant_id: assistantId,
      graph_id: assistantId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      config: {},
      metadata: {}
    } as Assistant)
  }, [])
  
  // 加载需求分析列表
  const loadRequirementAnalyses = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        project_id: projectId,
        ...(statusFilter !== "all" && { status: statusFilter }),
        ...(searchTerm && { search: searchTerm })
      })
      
      const response = await fetch(`/api/v2/requirement-analysis?${params}`)
      if (!response.ok) throw new Error("加载需求分析列表失败")
      
      const data = await response.json()
      setRequirementAnalyses(data.items || [])
    } catch (error) {
      console.error("加载需求分析列表失败:", error)
      toast.error("无法加载需求分析列表")
    } finally {
      setLoading(false)
    }
  }
  
  React.useEffect(() => {
    loadRequirementAnalyses()
  }, [projectId, statusFilter, searchTerm])
  
  // 删除需求分析
  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个需求分析吗？")) return
    
    try {
      const response = await fetch(`/api/v2/requirement-analysis/${id}`, {
        method: "DELETE"
      })
      
      if (!response.ok) throw new Error("删除需求分析失败")
      
      toast.success("需求分析已删除")
      loadRequirementAnalyses()
    } catch (error) {
      console.error("删除需求分析失败:", error)
      toast.error("无法删除需求分析")
    }
  }
  
  // 下载报告
  const handleDownload = async (id: string, identifier: string) => {
    try {
      const response = await fetch(`/api/v2/requirement-analysis/${id}/download?format=pdf`)
      if (!response.ok) throw new Error("下载报告失败")
      
      const data = await response.json()
      
      if (data.success && data.download_url) {
        window.open(data.download_url, "_blank")
        toast.success("需求分析报告下载已开始")
      }
    } catch (error) {
      console.error("下载报告失败:", error)
      toast.error("无法下载需求分析报告")
    }
  }
  
  // 查看详情
  const handleView = (id: string) => {
    router.push(`/projects/${projectId}/requirement-analysis/${id}`)
  }
  
  // 编辑
  const handleEdit = (ra: RequirementAnalysis) => {
    setSelectedRequirementAnalysis(ra)
    setEditDialogOpen(true)
  }
  
  // 打开 AI 聊天（从创建对话框回调）
  const handleOpenChat = (prompt: string) => {
    setAiChatInitialPrompt(prompt)
    setAiChatKey(prev => prev + 1) // 强制创建新对话
    setAiChatOpen(true)
    setCreateDialogOpen(false)
  }
  
  // 状态徽章
  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: "secondary",
      in_review: "default",
      approved: "outline",
      rejected: "destructive",
      archived: "outline"
    }
    
    const labels: Record<string, string> = {
      draft: "草稿",
      in_review: "评审中",
      approved: "已批准",
      rejected: "已拒绝",
      archived: "已归档"
    }
    
    return (
      <Badge variant={variants[status] || "default"}>
        {labels[status] || status}
      </Badge>
    )
  }
  
  // 质量评分显示
  const renderQualityScore = (score: number | null) => {
    if (score === null) return <span className="text-muted-foreground">-</span>
    
    let color = "text-red-500"
    if (score >= 80) color = "text-green-500"
    else if (score >= 60) color = "text-yellow-500"
    
    return <span className={`font-semibold ${color}`}>{score.toFixed(1)}</span>
  }
  
  return (
    <div className="relative h-full">
      <div className="container mx-auto py-6 space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">需求分析</h1>
            <p className="text-muted-foreground mt-1">
              智能分析需求文档，提取关键信息，生成分析报告
            </p>
          </div>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            创建需求分析
          </Button>
        </div>
        
        {/* 筛选和搜索 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索需求分析..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="筛选状态" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部状态</SelectItem>
                  <SelectItem value="draft">草稿</SelectItem>
                  <SelectItem value="in_review">评审中</SelectItem>
                  <SelectItem value="approved">已批准</SelectItem>
                  <SelectItem value="rejected">已拒绝</SelectItem>
                  <SelectItem value="archived">已归档</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                加载中...
              </div>
            ) : requirementAnalyses.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">暂无需求分析</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => setCreateDialogOpen(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  创建第一个需求分析
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>标识符</TableHead>
                    <TableHead>标题</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>质量评分</TableHead>
                    <TableHead>标签</TableHead>
                    <TableHead>创建时间</TableHead>
                    <TableHead className="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requirementAnalyses.map((ra) => (
                    <TableRow key={ra.id}>
                      <TableCell className="font-mono text-sm">
                        {ra.identifier}
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{ra.title}</div>
                          {ra.description && (
                            <div className="text-sm text-muted-foreground truncate max-w-md">
                              {ra.description}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(ra.status)}</TableCell>
                      <TableCell>{renderQualityScore(ra.quality_score)}</TableCell>
                      <TableCell>
                        <div className="flex gap-1 flex-wrap">
                          {ra.tags.slice(0, 2).map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {ra.tags.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{ra.tags.length - 2}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(ra.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>操作</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleView(ra.id)}>
                              <Eye className="mr-2 h-4 w-4" />
                              查看详情
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEdit(ra)}>
                              <Edit className="mr-2 h-4 w-4" />
                              编辑
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDownload(ra.id, ra.identifier)}>
                              <Download className="mr-2 h-4 w-4" />
                              下载报告
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={() => handleDelete(ra.id)}
                              className="text-red-600"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              删除
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
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
                // AI 生成需求分析后自动刷新列表
                loadRequirementAnalyses()
              }}
            />
          </ClientProvider>
        </div>
      )}
      
      {/* 创建对话框 */}
      <RequirementAnalysisCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        projectId={projectId}
        onSuccess={loadRequirementAnalyses}
        onOpenChat={handleOpenChat}
      />
      
      {/* 编辑对话框 */}
      {selectedRequirementAnalysis && (
        <RequirementAnalysisEditDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          requirementAnalysis={selectedRequirementAnalysis}
          onSuccess={loadRequirementAnalyses}
        />
      )}
    </div>
  )
}
