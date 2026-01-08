"use client";

import { useEffect, useMemo, useState } from "react";
import { Loader2 } from "lucide-react";

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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";

type RequirementAnalysisStatus = "draft" | "in_review" | "approved" | "rejected" | "archived";

export interface RequirementAnalysisEditDialogRequirementAnalysis {
  id: string;
  title: string;
  description: string | null;
  status: string;
  tags: string[];
}

interface RequirementAnalysisEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  requirementAnalysis: RequirementAnalysisEditDialogRequirementAnalysis;
  onSuccess: () => void;
}

export function RequirementAnalysisEditDialog({
  open,
  onOpenChange,
  requirementAnalysis,
  onSuccess,
}: RequirementAnalysisEditDialogProps) {
  const { toast } = useToast();

  const initialStatus = useMemo<RequirementAnalysisStatus>(() => {
    const status = requirementAnalysis.status as RequirementAnalysisStatus;
    if (["draft", "in_review", "approved", "rejected", "archived"].includes(status)) return status;
    return "draft";
  }, [requirementAnalysis.status]);

  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState(requirementAnalysis.title);
  const [description, setDescription] = useState(requirementAnalysis.description ?? "");
  const [status, setStatus] = useState<RequirementAnalysisStatus>(initialStatus);
  const [tags, setTags] = useState(requirementAnalysis.tags.join(", "));

  useEffect(() => {
    if (!open) return;
    setTitle(requirementAnalysis.title);
    setDescription(requirementAnalysis.description ?? "");
    setStatus(initialStatus);
    setTags(requirementAnalysis.tags.join(", "));
  }, [open, requirementAnalysis, initialStatus]);

  const handleSubmit = async () => {
    if (!title.trim()) {
      toast({ title: "验证失败", description: "请输入标题", variant: "destructive" });
      return;
    }

    const tagsArray = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    try {
      setLoading(true);

      const response = await fetch(`/api/v2/requirement-analysis/${requirementAnalysis.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() ? description.trim() : null,
          status,
          tags: tagsArray,
        }),
      });

      if (!response.ok) throw new Error("更新失败");

      toast({ title: "更新成功", description: "需求分析已更新" });
      onOpenChange(false);
      onSuccess();
    } catch (error) {
      console.error("更新需求分析失败:", error);
      toast({ title: "更新失败", description: "无法更新需求分析，请重试", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>编辑需求分析</DialogTitle>
          <DialogDescription>修改标题、描述、状态或标签。</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="ra-title">
              标题 <span className="text-red-500">*</span>
            </Label>
            <Input id="ra-title" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="ra-description">描述</Label>
            <Textarea
              id="ra-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label>状态</Label>
            <Select value={status} onValueChange={(v) => setStatus(v as RequirementAnalysisStatus)}>
              <SelectTrigger>
                <SelectValue placeholder="选择状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">草稿</SelectItem>
                <SelectItem value="in_review">评审中</SelectItem>
                <SelectItem value="approved">已批准</SelectItem>
                <SelectItem value="rejected">已拒绝</SelectItem>
                <SelectItem value="archived">已归档</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="ra-tags">标签（逗号分隔）</Label>
            <Input id="ra-tags" value={tags} onChange={(e) => setTags(e.target.value)} />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            取消
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            保存
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

