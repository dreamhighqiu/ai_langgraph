/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ZReE5RPT06ZDIwNDM3YzI=

import * as React from 'react'
import * as TabsPrimitive from '@radix-ui/react-tabs'

import { cn } from '@/lib/utils'
// eslint-disable  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ZReE5RPT06ZDIwNDM3YzI=

const Tabs = TabsPrimitive.Root

const TabsList = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      'bg-muted text-muted-foreground inline-flex h-10 items-center justify-center rounded-md p-1',
      className
    )}
    {...props}
  />
))
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'ring-offset-background focus-visible:ring-ring data-[state=active]:bg-background data-[state=active]:text-foreground inline-flex items-center justify-center rounded-sm px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-all focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 data-[state=active]:shadow-sm',
      className
    )}
    {...props}
  />
))
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

const TabsContent = React.forwardRef<
  React.ComponentRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      'ring-offset-background focus-visible:ring-ring focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none',
      'data-[state=inactive]:invisible data-[state=active]:visible',
      'h-full w-full',
      className
    )}
    // Force mounting of inactive tabs to preserve WebGL contexts
    forceMount
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent }
// NOTE  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ZReE5RPT06ZDIwNDM3YzI=
