/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import * as React from 'react'
import * as PopoverPrimitive from '@radix-ui/react-popover'

import { cn } from '@/lib/utils'

const Popover = PopoverPrimitive.Root
// NOTE  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YURFelJnPT06MTc1NmIzNDQ=

const PopoverTrigger = PopoverPrimitive.Trigger
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YURFelJnPT06MTc1NmIzNDQ=

// Define the props type to include positioning props
type PopoverContentProps = React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content> & {
  collisionPadding?: number | Partial<Record<'top' | 'right' | 'bottom' | 'left', number>>;
  sticky?: 'partial' | 'always';
  avoidCollisions?: boolean;
};

const PopoverContent = React.forwardRef<
  React.ComponentRef<typeof PopoverPrimitive.Content>,
  PopoverContentProps
>(({ className, align = 'center', sideOffset = 4, collisionPadding, sticky, avoidCollisions = false, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      collisionPadding={collisionPadding}
      sticky={sticky}
      avoidCollisions={avoidCollisions}
      className={cn(
        'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 rounded-md border p-4 shadow-md outline-none',
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
))
PopoverContent.displayName = PopoverPrimitive.Content.displayName

export { Popover, PopoverTrigger, PopoverContent }
