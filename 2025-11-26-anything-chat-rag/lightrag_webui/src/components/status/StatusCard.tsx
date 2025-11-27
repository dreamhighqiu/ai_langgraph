/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1UxaU1RPT06NmVmNTdmMzI=

import { LightragStatus } from '@/api/lightrag'
import { useTranslation } from 'react-i18next'
// NOTE  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1UxaU1RPT06NmVmNTdmMzI=

const StatusCard = ({ status }: { status: LightragStatus | null }) => {
  const { t } = useTranslation()
  if (!status) {
    return <div className="text-foreground text-xs">{t('graphPanel.statusCard.unavailable')}</div>
  }

  return (
    <div className="min-w-[300px] space-y-2 text-xs">
      <div className="space-y-1">
        <h4 className="font-medium">{t('graphPanel.statusCard.serverInfo')}</h4>
        <div className="text-foreground grid grid-cols-[160px_1fr] gap-1">
          <span>{t('graphPanel.statusCard.workingDirectory')}:</span>
          <span className="truncate">{status.working_directory}</span>
          <span>{t('graphPanel.statusCard.inputDirectory')}:</span>
          <span className="truncate">{status.input_directory}</span>
          <span>{t('graphPanel.statusCard.summarySettings')}:</span>
          <span>{status.configuration.summary_language} / LLM summary on {status.configuration.force_llm_summary_on_merge.toString()} fragments</span>
          <span>{t('graphPanel.statusCard.threshold')}:</span>
          <span>cosine {status.configuration.cosine_threshold} / rerank_score {status.configuration.min_rerank_score} / max_related {status.configuration.related_chunk_number}</span>
          <span>{t('graphPanel.statusCard.maxParallelInsert')}:</span>
          <span>{status.configuration.max_parallel_insert}</span>
        </div>
      </div>

      <div className="space-y-1">
        <h4 className="font-medium">{t('graphPanel.statusCard.llmConfig')}</h4>
        <div className="text-foreground grid grid-cols-[160px_1fr] gap-1">
          <span>{t('graphPanel.statusCard.llmBindingHost')}:</span>
          <span>{status.configuration.llm_binding_host}</span>
          <span>{t('graphPanel.statusCard.llmModel')}:</span>
          <span>{status.configuration.llm_binding}: {status.configuration.llm_model} (#{status.configuration.max_async} Async)</span>
        </div>
      </div>

      <div className="space-y-1">
        <h4 className="font-medium">{t('graphPanel.statusCard.embeddingConfig')}</h4>
        <div className="text-foreground grid grid-cols-[160px_1fr] gap-1">
          <span>{t('graphPanel.statusCard.embeddingBindingHost')}:</span>
          <span>{status.configuration.embedding_binding_host}</span>
          <span>{t('graphPanel.statusCard.embeddingModel')}:</span>
          <span>{status.configuration.embedding_binding}: {status.configuration.embedding_model} (#{status.configuration.embedding_func_max_async} Async * {status.configuration.embedding_batch_num} batches)</span>
        </div>
      </div>

      {status.configuration.enable_rerank && (
        <div className="space-y-1">
          <h4 className="font-medium">{t('graphPanel.statusCard.rerankerConfig')}</h4>
          <div className="text-foreground grid grid-cols-[160px_1fr] gap-1">
            <span>{t('graphPanel.statusCard.rerankerBindingHost')}:</span>
            <span>{status.configuration.rerank_binding_host || '-'}</span>
            <span>{t('graphPanel.statusCard.rerankerModel')}:</span>
            <span>{(status.configuration.rerank_binding || '-')} : {(status.configuration.rerank_model || '-')}</span>
          </div>
        </div>
      )}

      <div className="space-y-1">
        <h4 className="font-medium">{t('graphPanel.statusCard.storageConfig')}</h4>
        <div className="text-foreground grid grid-cols-[160px_1fr] gap-1">
          <span>{t('graphPanel.statusCard.kvStorage')}:</span>
          <span>{status.configuration.kv_storage}</span>
          <span>{t('graphPanel.statusCard.docStatusStorage')}:</span>
          <span>{status.configuration.doc_status_storage}</span>
          <span>{t('graphPanel.statusCard.graphStorage')}:</span>
          <span>{status.configuration.graph_storage}</span>
          <span>{t('graphPanel.statusCard.vectorStorage')}:</span>
          <span>{status.configuration.vector_storage}</span>
          <span>{t('graphPanel.statusCard.workspace')}:</span>
          <span>{status.configuration.workspace || '-'}</span>
          <span>{t('graphPanel.statusCard.maxGraphNodes')}:</span>
          <span>{status.configuration.max_graph_nodes || '-'}</span>
          {status.keyed_locks && (
            <>
              <span>{t('graphPanel.statusCard.lockStatus')}:</span>
              <span>
                mp {status.keyed_locks.current_status.pending_mp_cleanup}/{status.keyed_locks.current_status.total_mp_locks} |
                async {status.keyed_locks.current_status.pending_async_cleanup}/{status.keyed_locks.current_status.total_async_locks}
                (pid: {status.keyed_locks.process_id})
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
// @ts-expect-error  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1UxaU1RPT06NmVmNTdmMzI=

export default StatusCard
// TODO  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1UxaU1RPT06NmVmNTdmMzI=
