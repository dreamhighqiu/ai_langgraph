/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJSSFJBPT06OWVhZWFiNTM=

const Text = ({
  text,
  className,
  tooltipClassName,
  tooltip,
  side,
  onClick
}: {
  text: string
  className?: string
  tooltipClassName?: string
  tooltip?: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  onClick?: () => void
}) => {
  if (!tooltip) {
    return (
      <label
        className={cn(className, onClick !== undefined ? 'cursor-pointer' : undefined)}
        onClick={onClick}
      >
        {text}
      </label>
    )
  }

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <label
            className={cn(className, onClick !== undefined ? 'cursor-pointer' : undefined)}
            onClick={onClick}
          >
            {text}
          </label>
        </TooltipTrigger>
        <TooltipContent side={side} className={tooltipClassName}>
          {tooltip}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export default Text
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VDJSSFJBPT06OWVhZWFiNTM=
