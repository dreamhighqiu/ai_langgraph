/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U2paQ1pRPT06NTJlZGZmZDc=

import Button from '@/components/ui/Button'
import useTheme from '@/hooks/useTheme'
import { MoonIcon, SunIcon } from 'lucide-react'
import { useCallback } from 'react'
import { controlButtonVariant } from '@/lib/constants'
import { useTranslation } from 'react-i18next'

/**
 * Component that toggles the theme between light and dark.
 */
export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const setLight = useCallback(() => setTheme('light'), [setTheme])
  const setDark = useCallback(() => setTheme('dark'), [setTheme])
  const { t } = useTranslation()

  if (theme === 'dark') {
    return (
      <Button
        onClick={setLight}
        variant={controlButtonVariant}
        tooltip={t('header.themeToggle.switchToLight')}
        size="icon"
        side="bottom"
      >
        <MoonIcon />
      </Button>
    )
  }
  return (
    <Button
      onClick={setDark}
      variant={controlButtonVariant}
      tooltip={t('header.themeToggle.switchToDark')}
      size="icon"
      side="bottom"
    >
      <SunIcon />
    </Button>
  )
}
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U2paQ1pRPT06NTJlZGZmZDc=
