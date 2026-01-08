"use client"

/**
 * 缺陷分析创建对话框
 */

import { useState } from "react"
import { Upload, Sparkles, Loader2 } from "lucide-react"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"

interface DefectAnalysisCreateDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  projectId: string
  onSuccess: () => void
}

export function DefectAnalysisCreateDialog({
  open,
  onOpenChange,
  projectId,
  onSuccess
}: DefectAnalysisCreateDialogProps) {
  const { toast } = useToast()
  
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    severity: "medium",
    priority: "medium",
    defect_type: "functional",
    document_url: "",
    use_rag: false,
    rag_query: "",
    tags: ""
  })
  
  const [file, setFile] = useState<File | null>(null)
  
  // 处理文件上传
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      if (!formData.title) {
        const fileName = selectedFile.name.replace(/\.[^/.]+$/, "")
        setFormData(prev => ({ ...prev, title: fileName }))
      }
    }
  }
  
  // 上传文件到服务器
  const uploadFile = async (): Promise<string | null> => {
    if (!file) return null
    
    const uploadFormData = new FormData()
    uploadFormData.append("file", file)
    
    try {
      const response = await fetch("/api/v2/attachments/upload", {
        method: "POST",
        body: uploadFormData
      })
      
      if (!response.ok) throw new Error("文件上传失败")
      
      const data = await response.json()
      return data.url
    } catch (error) {
      console.error("文件上传失败:", error)
      toast({
        title: "上传失败",
        description: "文件上传失败，请重试",
        variant: "destructive"
      })
      return null
    }
  }
  
  // 提交表单
  const handleSubmit = async () => {
    if (!formData.title.trim()) {
      toast({
        title: "验证失败",
        description: "请输入缺陷分析标题",
        variant: "destructive"
      })
      return
    }
    
    try {
      setLoading(true)
      
      // 如果有文件，先上传
      let documentUrl = formData.document_url
      if (file) {
        documentUrl = await uploadFile() || ""
      }
      
      // 创建缺陷分析
      const tagsArray = formData.tags
        .split(",")
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
      
      const createData = {
        title: formData.title,
        description: formData.description || null,
        severity: formData.severity,
        priority: formData.priority,
        defect_type: formData.defect_type,
        document_url: documentUrl || null,
        document_type: file?.type || null,
        use_rag: formData.use_rag,
        rag_query: formData.rag_query || null,
        tags: tagsArray
      }
      
      const response = await fetch(`/api/v2/projects/${projectId}/defect-analysis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(createData)
      })
      
      if (!response.ok) throw new Error("创建缺陷分析失败")
      
      const result = await response.json()
      const defectAnalysisId = result.data.id
      
      toast({
        title: "创建成功",
        description: "缺陷分析已创建"
      })
      
      // 如果有文档，触发 AI 分析
      if (documentUrl) {
        fetch(`/api/v2/defect-analysis/${defectAnalysisId}/analyze`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            use_rag: formData.use_rag,
            rag_query: formData.rag_query || null
          })
        }).catch(error => {
          console.error("触发 AI 分析失败:", error)
        })
        
        toast({
          title: "AI 分析已启动",
          description: "系统正在分析缺陷报告，请稍后查看结果"
        })
      }
      
      // 重置表单并关闭对话框
      setFormData({
        title: "",
        description: "",
        severity: "medium",
        priority: "medium",
        defect_type: "functional",
        document_url: "",
        use_rag: false,
        rag_query: "",
        tags: ""
      })
      setFile(null)
      onOpenChange(false)
      onSuccess()
      
    } catch (error) {
      console.error("创建缺陷分析失败:", error)
      toast({
        title: "创建失败",
        description: "创建缺陷分析失败，请重试",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>创建缺陷分析</DialogTitle>
          <DialogDescription>
            上传缺陷报告，AI 将自动分析并提供修复建议
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* 标题 */}
          <div className="space-y-2">
            <Label htmlFor="title">
              标题 <span className="text-red-500">*</span>
            </Label>
            <Input
              id="title"
              placeholder="例如：用户登录模块缺陷分析"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>
          
          {/* 描述 */}
          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Textarea
              id="description"
              placeholder="简要描述缺陷的表现和影响..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
            />
          </div>
          
          {/* 严重程度和优先级 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="severity">严重程度</Label>
              <Select value={formData.severity} onValueChange={(value) => setFormData(prev => ({ ...prev, severity: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">关键</SelectItem>
                  <SelectItem value="high">高</SelectItem>
                  <SelectItem value="medium">中</SelectItem>
                  <SelectItem value="low">低</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="priority">优先级</Label>
              <Select value={formData.priority} onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="urgent">紧急</SelectItem>
                  <SelectItem value="high">高</SelectItem>
                  <SelectItem value="medium">中</SelectItem>
                  <SelectItem value="low">低</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {/* 缺陷类型 */}
          <div className="space-y-2">
            <Label htmlFor="defect_type">缺陷类型</Label>
            <Select value={formData.defect_type} onValueChange={(value) => setFormData(prev => ({ ...prev, defect_type: value }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="functional">功能缺陷</SelectItem>
                <SelectItem value="performance">性能问题</SelectItem>
                <SelectItem value="security">安全漏洞</SelectItem>
                <SelectItem value="ui">界面问题</SelectItem>
                <SelectItem value="compatibility">兼容性问题</SelectItem>
                <SelectItem value="data">数据问题</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* 文档上传 */}
          <div className="space-y-2">
            <Label htmlFor="file">缺陷报告文档</Label>
            <div className="flex items-center gap-2">
              <Input
                id="file"
                type="file"
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={handleFileChange}
                className="flex-1"
              />
              {file && (
                <div className="text-sm text-muted-foreground">
                  {file.name}
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              支持 PDF, Word, TXT, Markdown 格式
            </p>
          </div>
          
          {/* 文档 URL（可选） */}
          <div className="space-y-2">
            <Label htmlFor="document_url">或输入文档 URL</Label>
            <Input
              id="document_url"
              placeholder="https://example.com/defect-report.pdf"
              value={formData.document_url}
              onChange={(e) => setFormData(prev => ({ ...prev, document_url: e.target.value }))}
              disabled={!!file}
            />
          </div>
          
          {/* AI 分析选项 */}
          <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <Label className="text-base font-semibold">AI 分析选项</Label>
            </div>
            
            {/* RAG 检索 */}
            <div className="flex items-start space-x-3">
              <Checkbox
                id="use_rag"
                checked={formData.use_rag}
                onCheckedChange={(checked) =>
                  setFormData(prev => ({ ...prev, use_rag: checked as boolean }))
                }
              />
              <div className="space-y-1">
                <Label htmlFor="use_rag" className="cursor-pointer">
                  启用 RAG 上下文检索
                </Label>
                <p className="text-xs text-muted-foreground">
                  从知识库检索相似的历史缺陷和解决方案
                </p>
              </div>
            </div>
            
            {/* RAG 查询（可选） */}
            {formData.use_rag && (
              <div className="space-y-2 pl-7">
                <Label htmlFor="rag_query" className="text-sm">
                  自定义检索查询（可选）
                </Label>
                <Input
                  id="rag_query"
                  placeholder="例如：登录失败 认证错误"
                  value={formData.rag_query}
                  onChange={(e) => setFormData(prev => ({ ...prev, rag_query: e.target.value }))}
                />
              </div>
            )}
          </div>
          
          {/* 标签 */}
          <div className="space-y-2">
            <Label htmlFor="tags">标签</Label>
            <Input
              id="tags"
              placeholder="用逗号分隔，例如：登录,认证,紧急修复"
              value={formData.tags}
              onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            取消
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                创建中...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                创建并分析
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

