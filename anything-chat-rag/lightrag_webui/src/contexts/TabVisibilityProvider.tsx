/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WkV4MVF3PT06MGVmMmYyNjM=

import React, { useState, useEffect, useMemo } from 'react';
import { TabVisibilityContext } from './context';
import { TabVisibilityContextType } from './types';
import { useSettingsStore } from '@/stores/settings';

interface TabVisibilityProviderProps {
  children: React.ReactNode;
}
// eslint-disable  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WkV4MVF3PT06MGVmMmYyNjM=

/**
 * Provider component for the TabVisibility context
 * Manages the visibility state of tabs throughout the application
 */
export const TabVisibilityProvider: React.FC<TabVisibilityProviderProps> = ({ children }) => {
  // Get current tab from settings store
  const currentTab = useSettingsStore.use.currentTab();

  // Initialize visibility state with all tabs visible
  const [visibleTabs, setVisibleTabs] = useState<Record<string, boolean>>(() => ({
    'documents': true,
    'knowledge-graph': true,
    'retrieval': true,
    'api': true
  }));

  // Keep all tabs visible because we use CSS to control TAB visibility instead of React
  useEffect(() => {
    setVisibleTabs((prev) => ({
      ...prev,
      'documents': true,
      'knowledge-graph': true,
      'retrieval': true,
      'api': true
    }));
  }, [currentTab]);

  // Create the context value with memoization to prevent unnecessary re-renders
  const contextValue = useMemo<TabVisibilityContextType>(
    () => ({
      visibleTabs,
      setTabVisibility: (tabId: string, isVisible: boolean) => {
        setVisibleTabs((prev) => ({
          ...prev,
          [tabId]: isVisible,
        }));
      },
      isTabVisible: (tabId: string) => !!visibleTabs[tabId],
    }),
    [visibleTabs]
  );

  return (
    <TabVisibilityContext.Provider value={contextValue}>
      {children}
    </TabVisibilityContext.Provider>
  );
};
// TODO  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WkV4MVF3PT06MGVmMmYyNjM=

export default TabVisibilityProvider;
