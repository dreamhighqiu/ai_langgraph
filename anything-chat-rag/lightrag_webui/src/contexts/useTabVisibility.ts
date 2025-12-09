
// @ts-expect-error  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTNvM1F3PT06MDJlMDBjMTk=

import { useContext } from 'react';
import { TabVisibilityContext } from './context';
import { TabVisibilityContextType } from './types';

/**
 * Custom hook to access the tab visibility context
 * @returns The tab visibility context
 */
export const useTabVisibility = (): TabVisibilityContextType => {
  const context = useContext(TabVisibilityContext);

  if (!context) {
    throw new Error('useTabVisibility must be used within a TabVisibilityProvider');
  }

  return context;
};
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTNvM1F3PT06MDJlMDBjMTk=
