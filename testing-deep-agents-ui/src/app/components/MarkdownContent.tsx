
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJVMldRPT06ZmViYmE0OTg=

"use client";

import React, { useMemo, Suspense, lazy } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
// FIXME  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJVMldRPT06ZmViYmE0OTg=

// 懒加载代码高亮组件 - 减少初始加载体积
const SyntaxHighlighter = lazy(() =>
  import("react-syntax-highlighter").then((mod) => ({
    default: mod.Prism,
  }))
);

// 懒加载主题 - 按需加载
const loadOneDarkTheme = () =>
  import("react-syntax-highlighter/dist/esm/styles/prism").then(
    (mod) => mod.oneDark
  );

// 代码高亮组件缓存
let cachedTheme: any = null;

// 简单的代码块占位符
const CodePlaceholder = ({ children }: { children: React.ReactNode }) => (
  <pre className="rounded-md bg-slate-800 p-4 text-sm text-slate-100 overflow-x-auto">
    <code>{children}</code>
  </pre>
);

interface MarkdownContentProps {
  content: string;
  className?: string;
}
// NOTE  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJVMldRPT06ZmViYmE0OTg=

// 代码高亮组件 - 单独抽离以便懒加载
const CodeHighlighter = React.memo(
  ({
    language,
    children,
  }: {
    language: string;
    children: string;
  }) => {
    const [theme, setTheme] = React.useState<any>(cachedTheme);

    React.useEffect(() => {
      if (!cachedTheme) {
        loadOneDarkTheme().then((t) => {
          cachedTheme = t;
          setTheme(t);
        });
      }
    }, []);

    if (!theme) {
      return <CodePlaceholder>{children}</CodePlaceholder>;
    }

    return (
      <Suspense fallback={<CodePlaceholder>{children}</CodePlaceholder>}>
        <SyntaxHighlighter
          style={theme}
          language={language}
          PreTag="div"
          className="max-w-full rounded-md text-sm"
          wrapLines={true}
          wrapLongLines={true}
          lineProps={{
            style: {
              wordBreak: "break-all",
              whiteSpace: "pre-wrap",
              overflowWrap: "break-word",
            },
          }}
          customStyle={{
            margin: 0,
            maxWidth: "100%",
            overflowX: "auto",
            fontSize: "0.875rem",
          }}
        >
          {children}
        </SyntaxHighlighter>
      </Suspense>
    );
  }
);

CodeHighlighter.displayName = "CodeHighlighter";

export const MarkdownContent = React.memo<MarkdownContentProps>(
  ({ content, className = "" }) => {
    // 缓存 components 配置 - 避免每次渲染重新创建
    const components = useMemo(
      () => ({
        code({
          inline,
          className: codeClassName,
          children,
          ...props
        }: {
          inline?: boolean;
          className?: string;
          children?: React.ReactNode;
        }) {
          const match = /language-(\w+)/.exec(codeClassName || "");
          const codeString = String(children).replace(/\n$/, "");

          if (!inline && match) {
            return (
              <CodeHighlighter language={match[1]}>
                {codeString}
              </CodeHighlighter>
            );
          }

          return (
            <code
              className="bg-surface rounded-sm px-1 py-0.5 font-mono text-[0.9em]"
              {...props}
            >
              {children}
            </code>
          );
        },
        pre({ children }: { children?: React.ReactNode }) {
          return (
            <div className="my-4 max-w-full overflow-hidden last:mb-0">
              {children}
            </div>
          );
        },
        a({
          href,
          children,
        }: {
          href?: string;
          children?: React.ReactNode;
        }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary no-underline hover:underline"
            >
              {children}
            </a>
          );
        },
        blockquote({ children }: { children?: React.ReactNode }) {
          return (
            <blockquote className="text-primary/50 my-4 border-l-4 border-border pl-4 italic">
              {children}
            </blockquote>
          );
        },
        ul({ children }: { children?: React.ReactNode }) {
          return (
            <ul className="my-4 pl-6 [&>li:last-child]:mb-0 [&>li]:mb-1">
              {children}
            </ul>
          );
        },
        ol({ children }: { children?: React.ReactNode }) {
          return (
            <ol className="my-4 pl-6 [&>li:last-child]:mb-0 [&>li]:mb-1">
              {children}
            </ol>
          );
        },
        table({ children }: { children?: React.ReactNode }) {
          return (
            <div className="my-4 overflow-x-auto">
              <table className="[&_th]:bg-surface w-full border-collapse [&_td]:border [&_td]:border-border [&_td]:p-2 [&_th]:border [&_th]:border-border [&_th]:p-2 [&_th]:text-left [&_th]:font-semibold">
                {children}
              </table>
            </div>
          );
        },
        img(props: React.ImgHTMLAttributes<HTMLImageElement>) {
          return (
            <img
              {...props}
              alt={props.alt || ""}
              className="my-4 max-w-full rounded-md"
              loading="lazy"
            />
          );
        },
      }),
      []
    );

    // 缓存 remarkPlugins - 避免每次渲染重新创建数组
    const remarkPlugins = useMemo(() => [remarkGfm], []);

    return (
      <div
        className={cn(
          "prose min-w-0 max-w-full overflow-hidden break-words text-sm leading-relaxed text-inherit [&_h1:first-child]:mt-0 [&_h1]:mb-4 [&_h1]:mt-6 [&_h1]:font-semibold [&_h2:first-child]:mt-0 [&_h2]:mb-4 [&_h2]:mt-6 [&_h2]:font-semibold [&_h3:first-child]:mt-0 [&_h3]:mb-4 [&_h3]:mt-6 [&_h3]:font-semibold [&_h4:first-child]:mt-0 [&_h4]:mb-4 [&_h4]:mt-6 [&_h4]:font-semibold [&_h5:first-child]:mt-0 [&_h5]:mb-4 [&_h5]:mt-6 [&_h5]:font-semibold [&_h6:first-child]:mt-0 [&_h6]:mb-4 [&_h6]:mt-6 [&_h6]:font-semibold [&_p:last-child]:mb-0 [&_p]:mb-4",
          className
        )}
      >
        <ReactMarkdown
          remarkPlugins={remarkPlugins}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  },
  // 自定义比较函数 - 只有 content 和 className 变化时才重新渲染
  (prevProps, nextProps) =>
    prevProps.content === nextProps.content &&
    prevProps.className === nextProps.className
);

MarkdownContent.displayName = "MarkdownContent";
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJVMldRPT06ZmViYmE0OTg=
