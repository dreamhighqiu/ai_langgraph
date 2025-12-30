/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1RSME53PT06MjFiZDRiN2Y=

import * as React from 'react'
import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import { cn } from '@/lib/utils'

const TooltipProvider = TooltipPrimitive.Provider

const Tooltip = TooltipPrimitive.Root

const TooltipTrigger = TooltipPrimitive.Trigger
// FIXME  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1RSME53PT06MjFiZDRiN2Y=

const processTooltipContent = (content: string) => {
  if (typeof content !== 'string') return content
  return (
    <div className="relative top-0 pt-1 whitespace-pre-wrap break-words">
      {content}
    </div>
  )
}
// TODO  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1RSME53PT06MjFiZDRiN2Y=

const TooltipContent = React.forwardRef<
  React.ComponentRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content> & {
    side?: 'top' | 'right' | 'bottom' | 'left'
    align?: 'start' | 'center' | 'end'
  }
>(({ className, side = 'left', align = 'start', children, ...props }, ref) => {
  const contentRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = 0;
    }
  }, [children]);

  return (
    <TooltipPrimitive.Content
      ref={ref}
      side={side}
      align={align}
      className={cn(
        'bg-popover text-popover-foreground animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 max-h-[60vh] overflow-y-auto whitespace-pre-wrap break-words rounded-md border px-3 py-2 text-sm shadow-md z-60',
        className
      )}
      {...props}
    >
      {typeof children === 'string' ? processTooltipContent(children) : children}
    </TooltipPrimitive.Content>
  );
})
TooltipContent.displayName = TooltipPrimitive.Content.displayName

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
