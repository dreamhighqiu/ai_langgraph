/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0RkMmFBPT06Zjk2NzJlMzk=

import { useState, useCallback, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/AlertDialog'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { useSettingsStore } from '@/stores/settings'
import { useBackendState } from '@/stores/state'
import { InvalidApiKeyError, RequireApiKeError } from '@/api/lightrag'
// FIXME  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0RkMmFBPT06Zjk2NzJlMzk=

interface ApiKeyAlertProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
// NOTE  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0RkMmFBPT06Zjk2NzJlMzk=

const ApiKeyAlert = ({ open: opened, onOpenChange: setOpened }: ApiKeyAlertProps) => {
  const { t } = useTranslation()
  const apiKey = useSettingsStore.use.apiKey()
  const [tempApiKey, setTempApiKey] = useState<string>('')
  const message = useBackendState.use.message()

  useEffect(() => {
    setTempApiKey(apiKey || '')
  }, [apiKey, opened])

  useEffect(() => {
    if (message) {
      if (message.includes(InvalidApiKeyError) || message.includes(RequireApiKeError)) {
        setOpened(true)
      }
    }
  }, [message, setOpened])

  const setApiKey = useCallback(() => {
    useSettingsStore.setState({ apiKey: tempApiKey || null })
    setOpened(false)
  }, [tempApiKey, setOpened])

  const handleTempApiKeyChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setTempApiKey(e.target.value)
    },
    [setTempApiKey]
  )

  return (
    <AlertDialog open={opened} onOpenChange={setOpened}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('apiKeyAlert.title')}</AlertDialogTitle>
          <AlertDialogDescription>
            {t('apiKeyAlert.description')}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="flex flex-col gap-4">
          <form className="flex gap-2" onSubmit={(e) => e.preventDefault()}>
            <Input
              type="password"
              value={tempApiKey}
              onChange={handleTempApiKeyChange}
              placeholder={t('apiKeyAlert.placeholder')}
              className="max-h-full w-full min-w-0"
              autoComplete="off"
            />

            <Button onClick={setApiKey} variant="outline" size="sm">
              {t('apiKeyAlert.save')}
            </Button>
          </form>
          {message && (
            <div className="text-sm text-red-500">
              {message}
            </div>
          )}
        </div>
      </AlertDialogContent>
    </AlertDialog>
  )
}

export default ApiKeyAlert
// @ts-expect-error  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0RkMmFBPT06Zjk2NzJlMzk=
