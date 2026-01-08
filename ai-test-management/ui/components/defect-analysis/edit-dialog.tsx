"use client"

/**
 * 缺陷分析编辑对话框
 */

import { useState, useEffect } from "react"
import { Loader2 } from "lucide-react"

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"

interface DefectAnalysis {
  id: string
  title: string
  description: string | null
  severity: string | null
  priority: string | null
  defect_type: string | null
  status: string
  tags: string[]
}

interface DefectAnalysisEditDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defectAnalysis: DefectAnalysis
  onSuccess: () => void
}

export function DefectAnalysisEditDialog({
  open,
  onOpenChange,
  defectAnalysis,
  onSuccess
}: DefectAnalysisEditDialogProps) {
  const { toast } = useToast()
  
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    severity: "medium",
    priority: "medium",
    defect_type: "functional",
    status: "",
    tags: ""
  })
  
  // 初始化表单数据
  useEffect(() => {
    if (defectAnalysis) {
      setFormData({
        title: defectAnalysis.title,
        description: defectAnalysis.description || "",
        severity: defectAnalysis.severity || "medium",
        priority: defectAnalysis.priority || "medium",
        defect_type: defectAnalysis.defect_type || "functional",
        status: defectAnalysis.status,
        tags: defectAnalysis.tags.join(", ")
      })
    }
  }, [defectAnalysis])
  
  // 提交更新
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
      
      const tagsArray = formData.tags
        .split(",")
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
      
      const updateData = {
        title: formData.title,
        description: formData.description || null,
        severity: formData.severity,
        priority: formData.priority,
        defect_type: formData.defect_type,
        status: formData.status,
        tags: tagsArray
      }
      
      const response = await fetch(`/api/v2/defect-analysis/${defectAnalysis.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updateData)
      })
      
      if (!response.ok) throw new Error("更新缺陷分析失败")
      
      toast({
        title: "更新成功",
        description: "缺陷分析已更新"
      })
      
      onOpenChange(false)
      onSuccess()
      
    } catch (error) {
      console.error("更新缺陷分析失败:", error)
      toast({
        title: "更新失败",
        description: "更新缺陷分析失败，请重试",
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
          <DialogTitle>编辑缺陷分析</DialogTitle>
          <DialogDescription>
            更新缺陷分析的基本信息
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
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            />
          </div>
          
          {/* 描述 */}
          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Textarea
              id="description"
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
          
          {/* 状态 */}
          <div className="space-y-2">
            <Label htmlFor="status">状态</Label>
            <Select value={formData.status} onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}>
              <SelectTrigger>
                <SelectValue placeholder="选择状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">草稿</SelectItem>
                <SelectItem value="in_review">评审中</SelectItem>
                <SelectItem value="approved">已批准</SelectItem>
                <SelectItem value="rejected">已拒绝</SelectItem>
                <SelectItem value="resolved">已解决</SelectItem>
                <SelectItem value="archived">已归档</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* 标签 */}
          <div className="space-y-2">
            <Label htmlFor="tags">标签</Label>
            <Input
              id="tags"
              placeholder="用逗号分隔"
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
                更新中...
              </>
            ) : (
              "保存"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

