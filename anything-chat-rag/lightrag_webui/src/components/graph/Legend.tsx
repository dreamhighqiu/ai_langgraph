/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import React from 'react'
import { useTranslation } from 'react-i18next'
import { useGraphStore } from '@/stores/graph'
import { Card } from '@/components/ui/Card'
import { ScrollArea } from '@/components/ui/ScrollArea'
// NOTE  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUhvM1FRPT06N2I2MTM3MjI=

interface LegendProps {
  className?: string
}

const Legend: React.FC<LegendProps> = ({ className }) => {
  const { t } = useTranslation()
  const typeColorMap = useGraphStore.use.typeColorMap()

  if (!typeColorMap || typeColorMap.size === 0) {
    return null
  }

  return (
    <Card className={`p-2 max-w-xs ${className}`}>
      <h3 className="text-sm font-medium mb-2">{t('graphPanel.legend')}</h3>
      <ScrollArea className="max-h-80">
        <div className="flex flex-col gap-1">
          {Array.from(typeColorMap.entries()).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs truncate" title={type}>
                {t(`graphPanel.nodeTypes.${type.toLowerCase().replace(/\s+/g, '')}`, type)}
              </span>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  )
}

export default Legend
// NOTE  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUhvM1FRPT06N2I2MTM3MjI=
