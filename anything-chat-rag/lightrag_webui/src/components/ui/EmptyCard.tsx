/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVVabE5BPT06MTBhNTc1ZmQ=

import { cn } from '@/lib/utils'
import { Card, CardDescription, CardTitle } from '@/components/ui/Card'
import { FilesIcon } from 'lucide-react'

interface EmptyCardProps extends React.ComponentPropsWithoutRef<typeof Card> {
  title: string
  description?: string
  action?: React.ReactNode
  icon?: React.ComponentType<{ className?: string }>
}
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVVabE5BPT06MTBhNTc1ZmQ=

export default function EmptyCard({
  title,
  description,
  icon: Icon = FilesIcon,
  action,
  className,
  ...props
}: EmptyCardProps) {
  return (
    <Card
      className={cn(
        'flex w-full flex-col items-center justify-center space-y-6 bg-transparent p-16',
        className
      )}
      {...props}
    >
      <div className="mr-4 shrink-0 rounded-full border border-dashed p-4">
        <Icon className="text-muted-foreground size-8" aria-hidden="true" />
      </div>
      <div className="flex flex-col items-center gap-1.5 text-center">
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </div>
      {action ? action : null}
    </Card>
  )
}
