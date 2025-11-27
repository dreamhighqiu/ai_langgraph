/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import { useCallback } from 'react'
import { BookOpenIcon } from 'lucide-react'
import Button from '@/components/ui/Button'
import { controlButtonVariant } from '@/lib/constants'
import { useSettingsStore } from '@/stores/settings'
import { useTranslation } from 'react-i18next'
// FIXME  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVOWFVnPT06ZWUwNTkwMTA=

/**
 * Component that toggles legend visibility.
 */
const LegendButton = () => {
  const { t } = useTranslation()
  const showLegend = useSettingsStore.use.showLegend()
  const setShowLegend = useSettingsStore.use.setShowLegend()

  const toggleLegend = useCallback(() => {
    setShowLegend(!showLegend)
  }, [showLegend, setShowLegend])

  return (
    <Button
      variant={controlButtonVariant}
      onClick={toggleLegend}
      tooltip={t('graphPanel.sideBar.legendControl.toggleLegend')}
      size="icon"
    >
      <BookOpenIcon />
    </Button>
  )
}

export default LegendButton
// TODO  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVOWFVnPT06ZWUwNTkwMTA=
