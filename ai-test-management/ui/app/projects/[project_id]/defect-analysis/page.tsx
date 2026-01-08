"use client"

/**
 * 缺陷分析列表页面
 */

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import {
  Plus,
  Search,
  Filter,
  Download,
  Bug,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  AlertTriangle
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
import { useToast } from "@/components/ui/use-toast"

import { DefectAnalysisCreateDialog } from "@/components/defect-analysis/create-dialog"
import { DefectAnalysisEditDialog } from "@/components/defect-analysis/edit-dialog"

interface DefectAnalysis {
  id: string
  identifier: string
  title: string
  description: string | null
  severity: string | null
  priority: string | null
  defect_type: string | null
  status: string
  quality_score: number | null
  tags: string[]
  created_at: string
  updated_at: string
}

export default function DefectAnalysisPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  
  const projectId = params.project_id as string
  
  const [defectAnalyses, setDefectAnalyses] = useState<DefectAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [severityFilter, setSeverityFilter] = useState<string>("all")
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedDefectAnalysis, setSelectedDefectAnalysis] = useState<DefectAnalysis | null>(null)
  
  // 加载缺陷分析列表
  const loadDefectAnalyses = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        project_id: projectId,
        ...(statusFilter !== "all" && { status: statusFilter }),
        ...(severityFilter !== "all" && { severity: severityFilter }),
        ...(searchTerm && { search: searchTerm })
      })
      
      const response = await fetch(`/api/v2/defect-analysis?${params}`)
      if (!response.ok) throw new Error("加载缺陷分析列表失败")
      
      const data = await response.json()
      setDefectAnalyses(data.items || [])
    } catch (error) {
      console.error("加载缺陷分析列表失败:", error)
      toast({
        title: "加载失败",
        description: "无法加载缺陷分析列表",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadDefectAnalyses()
  }, [projectId, statusFilter, severityFilter, searchTerm])
  
  // 删除缺陷分析
  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个缺陷分析吗？")) return
    
    try {
      const response = await fetch(`/api/v2/defect-analysis/${id}`, {
        method: "DELETE"
      })
      
      if (!response.ok) throw new Error("删除缺陷分析失败")
      
      toast({
        title: "删除成功",
        description: "缺陷分析已删除"
      })
      
      loadDefectAnalyses()
    } catch (error) {
      console.error("删除缺陷分析失败:", error)
      toast({
        title: "删除失败",
        description: "无法删除缺陷分析",
        variant: "destructive"
      })
    }
  }
  
  // 下载报告
  const handleDownload = async (id: string) => {
    try {
      const response = await fetch(`/api/v2/defect-analysis/${id}/download?format=pdf`)
      if (!response.ok) throw new Error("下载报告失败")
      
      const data = await response.json()
      
      if (data.success && data.download_url) {
        window.open(data.download_url, "_blank")
        toast({
          title: "下载开始",
          description: "缺陷分析报告下载已开始"
        })
      }
    } catch (error) {
      console.error("下载报告失败:", error)
      toast({
        title: "下载失败",
        description: "无法下载缺陷分析报告",
        variant: "destructive"
      })
    }
  }
  
  // 查看详情
  const handleView = (id: string) => {
    router.push(`/projects/${projectId}/defect-analysis/${id}`)
  }
  
  // 编辑
  const handleEdit = (da: DefectAnalysis) => {
    setSelectedDefectAnalysis(da)
    setEditDialogOpen(true)
  }
  
  // 严重程度徽章
  const getSeverityBadge = (severity: string | null) => {
    if (!severity) return <span className="text-muted-foreground">-</span>
    
    const variants: Record<string, any> = {
      critical: { variant: "destructive", label: "关键" },
      high: { variant: "destructive", label: "高" },
      medium: { variant: "default", label: "中" },
      low: { variant: "secondary", label: "低" }
    }
    
    const config = variants[severity] || { variant: "default", label: severity }
    
    return (
      <Badge variant={config.variant as any}>
        {severity === "critical" && <AlertTriangle className="mr-1 h-3 w-3" />}
        {config.label}
      </Badge>
    )
  }
  
  // 优先级徽章
  const getPriorityBadge = (priority: string | null) => {
    if (!priority) return <span className="text-muted-foreground">-</span>
    
    const labels: Record<string, string> = {
      urgent: "紧急",
      high: "高",
      medium: "中",
      low: "低"
    }
    
    return (
      <Badge variant="outline">
        {labels[priority] || priority}
      </Badge>
    )
  }
  
  // 状态徽章
  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: "secondary",
      in_review: "default",
      approved: "outline",
      rejected: "destructive",
      resolved: "outline",
      archived: "outline"
    }
    
    const labels: Record<string, string> = {
      draft: "草稿",
      in_review: "评审中",
      approved: "已批准",
      rejected: "已拒绝",
      resolved: "已解决",
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
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">缺陷分析</h1>
          <p className="text-muted-foreground mt-1">
            智能分析缺陷报告，提供根因分析和修复建议
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          创建缺陷分析
        </Button>
      </div>
      
      {/* 筛选和搜索 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索缺陷分析..."
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
                <SelectItem value="resolved">已解决</SelectItem>
              </SelectContent>
            </Select>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="筛选严重程度" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部严重程度</SelectItem>
                <SelectItem value="critical">关键</SelectItem>
                <SelectItem value="high">高</SelectItem>
                <SelectItem value="medium">中</SelectItem>
                <SelectItem value="low">低</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : defectAnalyses.length === 0 ? (
            <div className="text-center py-8">
              <Bug className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">暂无缺陷分析</p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => setCreateDialogOpen(true)}
              >
                <Plus className="mr-2 h-4 w-4" />
                创建第一个缺陷分析
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>标识符</TableHead>
                  <TableHead>标题</TableHead>
                  <TableHead>严重程度</TableHead>
                  <TableHead>优先级</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>质量评分</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {defectAnalyses.map((da) => (
                  <TableRow key={da.id}>
                    <TableCell className="font-mono text-sm">
                      {da.identifier}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{da.title}</div>
                        {da.description && (
                          <div className="text-sm text-muted-foreground truncate max-w-md">
                            {da.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{getSeverityBadge(da.severity)}</TableCell>
                    <TableCell>{getPriorityBadge(da.priority)}</TableCell>
                    <TableCell>{getStatusBadge(da.status)}</TableCell>
                    <TableCell>{renderQualityScore(da.quality_score)}</TableCell>
                    <TableCell>
                      {new Date(da.created_at).toLocaleDateString()}
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
                          <DropdownMenuItem onClick={() => handleView(da.id)}>
                            <Eye className="mr-2 h-4 w-4" />
                            查看详情
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleEdit(da)}>
                            <Edit className="mr-2 h-4 w-4" />
                            编辑
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDownload(da.id)}>
                            <Download className="mr-2 h-4 w-4" />
                            下载报告
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => handleDelete(da.id)}
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
      
      {/* 创建对话框 */}
      <DefectAnalysisCreateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        projectId={projectId}
        onSuccess={loadDefectAnalyses}
      />
      
      {/* 编辑对话框 */}
      {selectedDefectAnalysis && (
        <DefectAnalysisEditDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          defectAnalysis={selectedDefectAnalysis}
          onSuccess={loadDefectAnalyses}
        />
      )}
    </div>
  )
}

