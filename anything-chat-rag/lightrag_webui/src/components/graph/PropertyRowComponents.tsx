/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUdSMVpBPT06NWU2NmU3ODI=

import { PencilIcon } from 'lucide-react'
import Text from '@/components/ui/Text'
import { useTranslation } from 'react-i18next'

interface PropertyNameProps {
  name: string
}

export const PropertyName = ({ name }: PropertyNameProps) => {
  const { t } = useTranslation()

  const getPropertyNameTranslation = (propName: string) => {
    const translationKey = `graphPanel.propertiesView.node.propertyNames.${propName}`
    const translation = t(translationKey)
    return translation === translationKey ? propName : translation
  }

  return (
    <span className="text-primary/60 tracking-wide whitespace-nowrap">
      {getPropertyNameTranslation(name)}
    </span>
  )
}

interface EditIconProps {
  onClick: () => void
}
// TODO  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUdSMVpBPT06NWU2NmU3ODI=

export const EditIcon = ({ onClick }: EditIconProps) => (
  <div>
    <PencilIcon
      className="h-3 w-3 text-gray-500 hover:text-gray-700 cursor-pointer"
      onClick={onClick}
    />
  </div>
)

interface PropertyValueProps {
  value: any
  onClick?: () => void
  tooltip?: string
}
// NOTE  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TUdSMVpBPT06NWU2NmU3ODI=

export const PropertyValue = ({ value, onClick, tooltip }: PropertyValueProps) => (
  <div className="flex items-center gap-1 overflow-hidden">
    <Text
      className="hover:bg-primary/20 rounded p-1 overflow-hidden text-ellipsis whitespace-nowrap"
      tooltipClassName="max-w-80 -translate-x-15"
      text={value}
      tooltip={tooltip || (typeof value === 'string' ? value : JSON.stringify(value, null, 2))}
      side="left"
      onClick={onClick}
    />
  </div>
)
