/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1hwaVV3PT06YzI0MGY3MTY=

import { useFullScreen } from '@react-sigma/core'
import { MaximizeIcon, MinimizeIcon } from 'lucide-react'
import { controlButtonVariant } from '@/lib/constants'
import Button from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

/**
 * Component that toggles full screen mode.
 */
const FullScreenControl = () => {
  const { isFullScreen, toggle } = useFullScreen()
  const { t } = useTranslation()

  return (
    <>
      {isFullScreen ? (
        <Button variant={controlButtonVariant} onClick={toggle} tooltip={t('graphPanel.sideBar.fullScreenControl.windowed')} size="icon">
          <MinimizeIcon />
        </Button>
      ) : (
        <Button variant={controlButtonVariant} onClick={toggle} tooltip={t('graphPanel.sideBar.fullScreenControl.fullScreen')} size="icon">
          <MaximizeIcon />
        </Button>
      )}
    </>
  )
}

export default FullScreenControl
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1hwaVV3PT06YzI0MGY3MTY=
