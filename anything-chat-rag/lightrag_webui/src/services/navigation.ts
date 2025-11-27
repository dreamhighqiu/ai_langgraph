/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UTFac2FBPT06MWYxNGRkMmQ=

import { NavigateFunction } from 'react-router-dom';
import { useAuthStore, useBackendState } from '@/stores/state';
import { useGraphStore } from '@/stores/graph';
import { useSettingsStore } from '@/stores/settings';
// TODO  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UTFac2FBPT06MWYxNGRkMmQ=

class NavigationService {
  private navigate: NavigateFunction | null = null;

  setNavigate(navigate: NavigateFunction) {
    this.navigate = navigate;
  }

  /**
   * Reset all application state to ensure a clean environment.
   * This function should be called when:
   * 1. User logs out
   * 2. Authentication token expires
   * 3. Direct access to login page
   *
   * @param preserveHistory If true, chat history will be preserved. Default is false.
   */
  resetAllApplicationState(preserveHistory = false) {
    console.log('Resetting all application state...');

    // Reset graph state
    const graphStore = useGraphStore.getState();
    const sigma = graphStore.sigmaInstance;
    graphStore.reset();
    graphStore.setGraphDataFetchAttempted(false);
    graphStore.setLabelsFetchAttempted(false);
    graphStore.setSigmaInstance(null);
    graphStore.setIsFetching(false); // Reset isFetching state to prevent data loading issues

    // Reset backend state
    useBackendState.getState().clear();

    // Reset retrieval history message only if preserveHistory is false
    if (!preserveHistory) {
      useSettingsStore.getState().setRetrievalHistory([]);
    }

    // Clear authentication state
    sessionStorage.clear();

    if (sigma) {
      sigma.getGraph().clear();
      sigma.kill();
      useGraphStore.getState().setSigmaInstance(null);
    }
  }

  /**
   * Navigate to login page and reset application state
   */
  navigateToLogin() {
    if (!this.navigate) {
      console.error('Navigation function not set');
      return;
    }

    // Store current username before logout for comparison during next login
    const currentUsername = useAuthStore.getState().username;
    if (currentUsername) {
      localStorage.setItem('LIGHTRAG-PREVIOUS-USER', currentUsername);
    }

    // Reset application state but preserve history
    // History will be cleared on next login if the user changes
    this.resetAllApplicationState(true);
    useAuthStore.getState().logout();

    this.navigate('/login');
  }

  navigateToHome() {
    if (!this.navigate) {
      console.error('Navigation function not set');
      return;
    }

    this.navigate('/');
  }
}
// TODO  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UTFac2FBPT06MWYxNGRkMmQ=

export const navigationService = new NavigationService();
// eslint-disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UTFac2FBPT06MWYxNGRkMmQ=
