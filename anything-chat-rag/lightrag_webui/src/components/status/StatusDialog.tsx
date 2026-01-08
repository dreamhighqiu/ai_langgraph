

import { LightragStatus } from '@/api/lightrag'
import { useTranslation } from 'react-i18next'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/Dialog'
import StatusCard from './StatusCard'
// FIXME  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsclFRPT06MGMzZGFmMjQ=

interface StatusDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  status: LightragStatus | null
}
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsclFRPT06MGMzZGFmMjQ=

const StatusDialog = ({ open, onOpenChange, status }: StatusDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>{t('graphPanel.statusDialog.title')}</DialogTitle>
          <DialogDescription>
            {t('graphPanel.statusDialog.description')}
          </DialogDescription>
        </DialogHeader>
        <StatusCard status={status} />
      </DialogContent>
    </Dialog>
  )
}

export default StatusDialog
