"use client"

/**
 * 需求分析创建对话框
 * 
 * 功能：
 * - 上传需求文档
 * - 配置 AI 分析选项（包括 RAG）
 * - 触发智能分析
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
import { useToast } from "@/components/ui/use-toast"

interface RequirementAnalysisCreateDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  projectId: string
  onSuccess: () => void
  onOpenChat?: (prompt: string) => void  // 新增：打开 AI 聊天的回调
}

export function RequirementAnalysisCreateDialog({
  open,
  onOpenChange,
  projectId,
  onSuccess,
  onOpenChat  // 新增回调
}: RequirementAnalysisCreateDialogProps) {
  const { toast } = useToast()
  
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
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
      // 自动填充标题（如果未填写）
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
      toast({ title: "请输入需求分析标题", variant: "destructive" })
      return
    }
    
    // 如果提供了 onOpenChat 回调，使用聊天界面
    if (onOpenChat) {
      const chatPrompt = `请帮我分析需求文档并生成需求分析报告。

需求标题：${formData.title.trim()}
需求描述：${formData.description || "无"}
${formData.use_rag ? "使用 RAG 检索：是（请先从知识库检索相关信息）" : "使用 RAG 检索：否"}
${formData.rag_query ? `RAG 查询：${formData.rag_query}` : ""}

请根据以上需求进行分析，包括：
1. 提取需求概述
2. 分析功能需求和非功能需求
3. 生成用户故事
4. 定义验收标准
5. 识别依赖关系和风险
6. 提供质量评分

${formData.use_rag ? "注意：请先使用 rag_query_tool 从知识库检索相关信息，然后基于检索结果进行分析。" : ""}`

      onOpenChat(chatPrompt)
      
      // 重置表单
      setFormData({
        title: "",
        description: "",
        document_url: "",
        use_rag: false,
        rag_query: "",
        tags: ""
      })
      setFile(null)
      return
    }
    
    // 否则使用原来的方式（直接创建）
    try {
      setLoading(true)
      
      // 如果有文件，先上传
      let documentUrl = formData.document_url
      if (file) {
        documentUrl = await uploadFile() || ""
      }
      
      // 创建需求分析
      const tagsArray = formData.tags
        .split(",")
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
      
      const createData = {
        title: formData.title,
        description: formData.description || null,
        document_url: documentUrl || null,
        document_type: file?.type || null,
        use_rag: formData.use_rag,
        rag_query: formData.rag_query || null,
        tags: tagsArray
      }
      
      const response = await fetch(`/api/v2/projects/${projectId}/requirement-analysis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(createData)
      })
      
      if (!response.ok) throw new Error("创建需求分析失败")
      
      const result = await response.json()
      
      toast({ title: "需求分析已创建" })
      
      // 重置表单并关闭对话框
      setFormData({
        title: "",
        description: "",
        document_url: "",
        use_rag: false,
        rag_query: "",
        tags: ""
      })
      setFile(null)
      onOpenChange(false)
      onSuccess()
      
    } catch (error) {
      console.error("创建需求分析失败:", error)
      toast({ title: "创建需求分析失败，请重试", variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>创建需求分析</DialogTitle>
          <DialogDescription>
            上传需求文档，AI 将自动分析并生成分析报告
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
              placeholder="例如：电商平台用户管理模块需求分析"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>
          
          {/* 描述 */}
          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Textarea
              id="description"
              placeholder="简要描述需求分析的内容和目标..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
            />
          </div>
          
          {/* 文档上传 */}
          <div className="space-y-2">
            <Label htmlFor="file">需求文档</Label>
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
              placeholder="https://example.com/requirement.pdf"
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
                  从知识库检索相关的技术规范和历史需求，提供更准确的分析
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
                  placeholder="例如：用户认证和授权相关规范"
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
              placeholder="用逗号分隔，例如：用户管理,V2.0,高优先级"
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
                {onOpenChat ? "开始 AI 分析" : "创建需求分析"}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

