/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import React, { useEffect } from 'react';
import { useTabVisibility } from '@/contexts/useTabVisibility';
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGs5MGJRPT06NTRmZmM5NTU=

interface TabContentProps {
  tabId: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * TabContent component that manages visibility based on tab selection
 * Works with the TabVisibilityContext to show/hide content based on active tab
 */
const TabContent: React.FC<TabContentProps> = ({ tabId, children, className = '' }) => {
  const { isTabVisible, setTabVisibility } = useTabVisibility();
  const isVisible = isTabVisible(tabId);

  // Register this tab with the context when mounted
  useEffect(() => {
    setTabVisibility(tabId, true);

    // Cleanup when unmounted
    return () => {
      setTabVisibility(tabId, false);
    };
  }, [tabId, setTabVisibility]);

  // Use CSS to hide content instead of not rendering it
  // This prevents components from unmounting when tabs are switched
  return (
    <div className={`${className} ${isVisible ? '' : 'hidden'}`}>
      {children}
    </div>
  );
};

export default TabContent;
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGs5MGJRPT06NTRmZmM5NTU=
