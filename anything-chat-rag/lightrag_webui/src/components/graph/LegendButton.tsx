

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
