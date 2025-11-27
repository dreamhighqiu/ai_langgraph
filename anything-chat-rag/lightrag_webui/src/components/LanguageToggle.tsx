/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UW1WdWNnPT06MzQ5ZmJiOTk=

import Button from '@/components/ui/Button'
import { useCallback } from 'react'
import { controlButtonVariant } from '@/lib/constants'
import { useTranslation } from 'react-i18next'
import { useSettingsStore } from '@/stores/settings'

/**
 * Component that toggles the language between English and Chinese.
 */
export default function LanguageToggle() {
  const { i18n } = useTranslation()
  const currentLanguage = i18n.language
  const setLanguage = useSettingsStore.use.setLanguage()

  const setEnglish = useCallback(() => {
    i18n.changeLanguage('en')
    setLanguage('en')
  }, [i18n, setLanguage])

  const setChinese = useCallback(() => {
    i18n.changeLanguage('zh')
    setLanguage('zh')
  }, [i18n, setLanguage])

  if (currentLanguage === 'zh') {
    return (
      <Button
        onClick={setEnglish}
        variant={controlButtonVariant}
        tooltip="Switch to English"
        size="icon"
        side="bottom"
      >
        中
      </Button>
    )
  }
  return (
    <Button
      onClick={setChinese}
      variant={controlButtonVariant}
      tooltip="切换到中文"
      size="icon"
      side="bottom"
    >
      EN
    </Button>
  )
}
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UW1WdWNnPT06MzQ5ZmJiOTk=
