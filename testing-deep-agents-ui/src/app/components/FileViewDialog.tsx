
// TODO  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZURoU1l3PT06YzA0ZjNiYmY=

"use client";
// TODO  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZURoU1l3PT06YzA0ZjNiYmY=

import React, { useMemo, useCallback, useState, useEffect, Suspense, lazy } from "react";
import { FileText, Copy, Download, Edit, Save, X, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { MarkdownContent } from "@/app/components/MarkdownContent";
import type { FileItem } from "@/app/types/types";
import useSWRMutation from "swr/mutation";

// 懒加载代码高亮组件
const SyntaxHighlighter = lazy(() =>
  import("react-syntax-highlighter").then((mod) => ({
    default: mod.Prism,
  }))
);

// 懒加载主题
let cachedTheme: any = null;
const loadOneDarkTheme = () =>
  import("react-syntax-highlighter/dist/esm/styles/prism").then(
    (mod) => mod.oneDark
  );

const LANGUAGE_MAP: Record<string, string> = {
  js: "javascript",
  jsx: "javascript",
  ts: "typescript",
  tsx: "typescript",
  py: "python",
  rb: "ruby",
  go: "go",
  rs: "rust",
  java: "java",
  cpp: "cpp",
  c: "c",
  cs: "csharp",
  php: "php",
  swift: "swift",
  kt: "kotlin",
  scala: "scala",
  sh: "bash",
  bash: "bash",
  zsh: "bash",
  json: "json",
  xml: "xml",
  html: "html",
  css: "css",
  scss: "scss",
  sass: "sass",
  less: "less",
  sql: "sql",
  yaml: "yaml",
  yml: "yaml",
  toml: "toml",
  ini: "ini",
  dockerfile: "dockerfile",
  makefile: "makefile",
};
// FIXME  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZURoU1l3PT06YzA0ZjNiYmY=

// 代码高亮占位符
const CodePlaceholder = ({ children }: { children: string }) => (
  <pre className="rounded-md bg-slate-800 p-4 text-sm text-slate-100 overflow-x-auto">
    <code>{children}</code>
  </pre>
);

// 懒加载的代码高亮组件
const LazyCodeHighlighter = React.memo(
  ({ language, content }: { language: string; content: string }) => {
    const [theme, setTheme] = useState<any>(cachedTheme);

    useEffect(() => {
      if (!cachedTheme) {
        loadOneDarkTheme().then((t) => {
          cachedTheme = t;
          setTheme(t);
        });
      }
    }, []);

    if (!theme) {
      return <CodePlaceholder>{content}</CodePlaceholder>;
    }

    return (
      <Suspense fallback={<CodePlaceholder>{content}</CodePlaceholder>}>
        <SyntaxHighlighter
          language={language}
          style={theme}
          customStyle={{
            margin: 0,
            borderRadius: "0.5rem",
            fontSize: "0.875rem",
          }}
          showLineNumbers
          wrapLines={true}
          lineProps={{
            style: {
              whiteSpace: "pre-wrap",
            },
          }}
        >
          {content}
        </SyntaxHighlighter>
      </Suspense>
    );
  }
);

LazyCodeHighlighter.displayName = "LazyCodeHighlighter";

export const FileViewDialog = React.memo<{
  file: FileItem | null;
  onSaveFile: (fileName: string, content: string) => Promise<void>;
  onClose: () => void;
  editDisabled: boolean;
}>(({ file, onSaveFile, onClose, editDisabled }) => {
  const [isEditingMode, setIsEditingMode] = useState(file === null);
  const [fileName, setFileName] = useState(String(file?.path || ""));
  const [fileContent, setFileContent] = useState(String(file?.content || ""));

  const fileUpdate = useSWRMutation(
    { kind: "files-update", fileName, fileContent },
    async ({ fileName, fileContent }) => {
      if (!fileName || !fileContent) return;
      return await onSaveFile(fileName, fileContent);
    },
    {
      onSuccess: () => setIsEditingMode(false),
      onError: (error) => toast.error(`保存文件失败: ${error}`),
    }
  );

  useEffect(() => {
    setFileName(String(file?.path || ""));
    setFileContent(String(file?.content || ""));
    setIsEditingMode(file === null);
  }, [file]);

  const fileExtension = useMemo(() => {
    const fileNameStr = String(fileName || "");
    return fileNameStr.split(".").pop()?.toLowerCase() || "";
  }, [fileName]);

  const isMarkdown = useMemo(() => {
    return fileExtension === "md" || fileExtension === "markdown";
  }, [fileExtension]);

  const language = useMemo(() => {
    return LANGUAGE_MAP[fileExtension] || "text";
  }, [fileExtension]);

  const handleCopy = useCallback(() => {
    if (fileContent) {
      navigator.clipboard.writeText(fileContent);
      toast.success("已复制到剪贴板");
    }
  }, [fileContent]);

  const handleDownload = useCallback(() => {
    if (fileContent && fileName) {
      const blob = new Blob([fileContent], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [fileContent, fileName]);

  const handleEdit = useCallback(() => {
    setIsEditingMode(true);
  }, []);

  const handleCancel = useCallback(() => {
    if (file === null) {
      onClose();
    } else {
      setFileName(String(file.path));
      setFileContent(String(file.content));
      setIsEditingMode(false);
    }
  }, [file, onClose]);

  const fileNameIsValid = useMemo(() => {
    return (
      fileName.trim() !== "" &&
      !fileName.includes("/") &&
      !fileName.includes(" ")
    );
  }, [fileName]);

  const handleTriggerUpdate = useCallback(() => {
    fileUpdate.trigger();
  }, [fileUpdate]);

  return (
    <Dialog
      open={true}
      onOpenChange={onClose}
    >
      <DialogContent className="flex h-[80vh] max-h-[80vh] min-w-[60vw] flex-col p-6">
        <DialogTitle className="sr-only">
          {file?.path || "新建文件"}
        </DialogTitle>
        <div className="mb-4 flex items-center justify-between border-b border-border pb-4">
          <div className="flex min-w-0 items-center gap-2">
            <FileText className="text-primary/50 h-5 w-5 shrink-0" />
            {isEditingMode && file === null ? (
              <Input
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                placeholder="输入文件名..."
                className="text-base font-medium"
                aria-invalid={!fileNameIsValid}
              />
            ) : (
              <span className="overflow-hidden text-ellipsis whitespace-nowrap text-base font-medium text-primary">
                {file?.path}
              </span>
            )}
          </div>
          <div className="flex shrink-0 items-center gap-1">
            {!isEditingMode && (
              <>
                <Button
                  onClick={handleEdit}
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                  disabled={editDisabled}
                >
                  <Edit
                    size={16}
                    className="mr-1"
                  />
                  编辑
                </Button>
                <Button
                  onClick={handleCopy}
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                >
                  <Copy
                    size={16}
                    className="mr-1"
                  />
                  复制
                </Button>
                <Button
                  onClick={handleDownload}
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                >
                  <Download
                    size={16}
                    className="mr-1"
                  />
                  下载
                </Button>
              </>
            )}
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-hidden">
          {isEditingMode ? (
            <Textarea
              value={fileContent}
              onChange={(e) => setFileContent(e.target.value)}
              placeholder="输入文件内容..."
              className="h-full min-h-[400px] resize-none font-mono text-sm"
            />
          ) : (
            <ScrollArea className="bg-surface h-full rounded-md">
              <div className="p-4">
                {fileContent ? (
                  isMarkdown ? (
                    <div className="rounded-md p-6">
                      <MarkdownContent content={fileContent} />
                    </div>
                  ) : (
                    <LazyCodeHighlighter
                      language={language}
                      content={fileContent}
                    />
                  )
                ) : (
                  <div className="flex items-center justify-center p-12">
                    <p className="text-sm text-muted-foreground">
                      文件为空
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </div>
        {isEditingMode && (
          <div className="mt-4 flex justify-end gap-2 border-t border-border pt-4">
            <Button
              onClick={handleCancel}
              variant="outline"
              size="sm"
            >
              <X
                size={16}
                className="mr-1"
              />
              取消
            </Button>
            <Button
              onClick={handleTriggerUpdate}
              size="sm"
              disabled={
                fileUpdate.isMutating ||
                !fileName.trim() ||
                !fileContent.trim() ||
                !fileNameIsValid
              }
            >
              {fileUpdate.isMutating ? (
                <Loader2
                  size={16}
                  className="mr-1 animate-spin"
                />
              ) : (
                <Save
                  size={16}
                  className="mr-1"
                />
              )}
              保存
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
});
// TODO  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZURoU1l3PT06YzA0ZjNiYmY=

FileViewDialog.displayName = "FileViewDialog";
