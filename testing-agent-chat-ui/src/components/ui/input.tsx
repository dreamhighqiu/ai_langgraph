/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(智能测试) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(智能测试)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import * as React from "react";
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldWMVFRPT06NjkwMjc5YjM=

import { cn } from "@/lib/utils";
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldWMVFRPT06NjkwMjc5YjM=

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "border-input file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
