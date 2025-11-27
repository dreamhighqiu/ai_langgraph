/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

import { createContext, useEffect } from 'react'
import { Theme, useSettingsStore } from '@/stores/settings'
// FIXME  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UzBaaGN3PT06NGEzMDA4ZWI=

type ThemeProviderProps = {
  children: React.ReactNode
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}
// eslint-disable  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UzBaaGN3PT06NGEzMDA4ZWI=

const initialState: ThemeProviderState = {
  theme: 'system',
  setTheme: () => null
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)
// NOTE  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UzBaaGN3PT06NGEzMDA4ZWI=

/**
 * Component that provides the theme state and setter function to its children.
 */
export default function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const theme = useSettingsStore.use.theme()
  const setTheme = useSettingsStore.use.setTheme()

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = (e: MediaQueryListEvent) => {
        root.classList.remove('light', 'dark')
        root.classList.add(e.matches ? 'dark' : 'light')
      }

      root.classList.add(mediaQuery.matches ? 'dark' : 'light')
      mediaQuery.addEventListener('change', handleChange)

      return () => mediaQuery.removeEventListener('change', handleChange)
    } else {
      root.classList.add(theme)
    }
  }, [theme])

  const value = {
    theme,
    setTheme
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export { ThemeProviderContext }
