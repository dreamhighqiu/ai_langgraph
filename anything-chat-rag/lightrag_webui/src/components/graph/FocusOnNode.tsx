/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// NOTE  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vlhjd2J3PT06M2RkMmQxOGQ=

import { useCamera, useSigma } from '@react-sigma/core'
import { useEffect } from 'react'
import { useGraphStore } from '@/stores/graph'
// FIXME  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vlhjd2J3PT06M2RkMmQxOGQ=

/**
 * Component that highlights a node and centers the camera on it.
 */
const FocusOnNode = ({ node, move }: { node: string | null; move?: boolean }) => {
  const sigma = useSigma()
  const { gotoNode } = useCamera()

  /**
   * When the selected item changes, highlighted the node and center the camera on it.
   */
  useEffect(() => {
    const graph = sigma.getGraph();

    if (move) {
      if (node && graph.hasNode(node)) {
        try {
          graph.setNodeAttribute(node, 'highlighted', true);
          gotoNode(node);
        } catch (error) {
          console.error('Error focusing on node:', error);
        }
      } else {
        // If no node is selected but move is true, reset to default view
        sigma.setCustomBBox(null);
        sigma.getCamera().animate({ x: 0.5, y: 0.5, ratio: 1 }, { duration: 0 });
      }
      useGraphStore.getState().setMoveToSelectedNode(false);
    } else if (node && graph.hasNode(node)) {
      try {
        graph.setNodeAttribute(node, 'highlighted', true);
      } catch (error) {
        console.error('Error highlighting node:', error);
      }
    }

    return () => {
      if (node && graph.hasNode(node)) {
        try {
          graph.setNodeAttribute(node, 'highlighted', false);
        } catch (error) {
          console.error('Error cleaning up node highlight:', error);
        }
      }
    }
  }, [node, move, sigma, gotoNode])

  return null
}
// NOTE  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vlhjd2J3PT06M2RkMmQxOGQ=

export default FocusOnNode
