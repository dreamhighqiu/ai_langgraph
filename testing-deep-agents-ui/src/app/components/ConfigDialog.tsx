

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StandaloneConfig, GraphInfo, fetchAvailableGraphs, getDefaultGraphs, DEFAULT_CONFIG } from "@/lib/config";
import { Loader2, RefreshCw, Sparkles } from "lucide-react";

interface ConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (config: StandaloneConfig) => void;
  initialConfig?: StandaloneConfig;
}

export function ConfigDialog({
  open,
  onOpenChange,
  onSave,
  initialConfig,
}: ConfigDialogProps) {
  const [deploymentUrl, setDeploymentUrl] = useState(
    initialConfig?.deploymentUrl || DEFAULT_CONFIG.deploymentUrl
  );
  const [assistantId, setAssistantId] = useState(
    initialConfig?.assistantId || DEFAULT_CONFIG.assistantId
  );
  const [langsmithApiKey, setLangsmithApiKey] = useState(
    initialConfig?.langsmithApiKey || ""
  );
  
  // Graph 列表状态
  const [graphs, setGraphs] = useState<GraphInfo[]>(getDefaultGraphs());
  const [isLoadingGraphs, setIsLoadingGraphs] = useState(false);
  const [graphsError, setGraphsError] = useState<string | null>(null);

  // 加载可用的 graphs
  const loadGraphs = useCallback(async (url: string) => {
    if (!url) return;
    
    setIsLoadingGraphs(true);
    setGraphsError(null);
    
    try {
      const availableGraphs = await fetchAvailableGraphs(url);
      if (availableGraphs.length > 0) {
        setGraphs(availableGraphs);
      } else {
        setGraphs(getDefaultGraphs());
      }
    } catch (error) {
      console.error("Failed to load graphs:", error);
      setGraphsError("无法连接到服务器，使用默认列表");
      setGraphs(getDefaultGraphs());
    } finally {
      setIsLoadingGraphs(false);
    }
  }, []);

  useEffect(() => {
    if (open && initialConfig) {
      setDeploymentUrl(initialConfig.deploymentUrl || DEFAULT_CONFIG.deploymentUrl);
      setAssistantId(initialConfig.assistantId || DEFAULT_CONFIG.assistantId);
      setLangsmithApiKey(initialConfig.langsmithApiKey || "");
    }
  }, [open, initialConfig]);

  // 当对话框打开时加载 graphs
  useEffect(() => {
    if (open && deploymentUrl) {
      loadGraphs(deploymentUrl);
    }
  }, [open, deploymentUrl, loadGraphs]);

  const handleSave = () => {
    if (!deploymentUrl || !assistantId) {
      alert("请填写所有必填字段");
      return;
    }

    onSave({
      deploymentUrl,
      assistantId,
      langsmithApiKey: langsmithApiKey || undefined,
    });
    onOpenChange(false);
  };

  const handleRefreshGraphs = () => {
    loadGraphs(deploymentUrl);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px] rounded-2xl border-0 shadow-2xl bg-gradient-to-b from-white to-slate-50/80 dark:from-slate-900 dark:to-slate-950">
        <DialogHeader className="space-y-3 pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <DialogTitle className="text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                智能体配置
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-500 dark:text-slate-400">
                配置您的智能体部署设置
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>
        
        <div className="grid gap-5 py-4">
          {/* 部署 URL */}
          <div className="grid gap-2.5">
            <Label htmlFor="deploymentUrl" className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              部署 URL
            </Label>
            <Input
              id="deploymentUrl"
              placeholder="http://localhost:2025"
              value={deploymentUrl}
              onChange={(e) => setDeploymentUrl(e.target.value)}
              className="h-11 rounded-xl border-slate-200 bg-white/80 px-4 shadow-sm transition-all focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-800/80"
            />
          </div>
          
          {/* 智能体选择 */}
          <div className="grid gap-2.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="assistantId" className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                选择智能体
              </Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleRefreshGraphs}
                disabled={isLoadingGraphs}
                className="h-7 px-2 text-xs text-slate-500 hover:text-emerald-600"
              >
                {isLoadingGraphs ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="h-3.5 w-3.5" />
                )}
                <span className="ml-1.5">刷新</span>
              </Button>
            </div>
            
            <Select value={assistantId} onValueChange={setAssistantId}>
              <SelectTrigger className="h-11 rounded-xl border-slate-200 bg-white/80 px-4 shadow-sm transition-all focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-800/80">
                <SelectValue placeholder="选择一个智能体" />
              </SelectTrigger>
              <SelectContent className="rounded-xl border-slate-200 shadow-xl dark:border-slate-700">
                {graphs.map((graph) => (
                  <SelectItem
                    key={graph.id}
                    value={graph.id}
                    className="cursor-pointer rounded-lg py-3 transition-colors hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{graph.name}</span>
                      {graph.description && (
                        <span className="text-xs text-slate-500">{graph.description}</span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {graphsError && (
              <p className="text-xs text-amber-600 dark:text-amber-400">{graphsError}</p>
            )}
          </div>
        </div>
        
        <DialogFooter className="gap-3 pt-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="h-10 rounded-xl border-slate-200 px-5 font-medium transition-all hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          >
            取消
          </Button>
          <Button
            onClick={handleSave}
            className="h-10 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-6 font-medium text-white shadow-lg shadow-emerald-500/25 transition-all hover:from-emerald-600 hover:to-teal-700 hover:shadow-xl hover:shadow-emerald-500/30"
          >
            保存配置
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
