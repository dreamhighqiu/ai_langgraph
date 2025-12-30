/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGxKek5RPT06ZGE5ZDljNjc=

import * as React from 'react'
import { cn } from '@/lib/utils'

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  className?: string
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'border-input file:text-foreground placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:ring-1 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-none',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'
// NOTE  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGxKek5RPT06ZGE5ZDljNjc=

export default Textarea
