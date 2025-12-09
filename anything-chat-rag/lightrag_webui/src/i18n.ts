

import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { useSettingsStore } from '@/stores/settings'
// TODO  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y1dneVR3PT06NmI1MjY0ZDU=

import en from './locales/en.json'
import zh from './locales/zh.json'
import fr from './locales/fr.json'
import ar from './locales/ar.json'
import zh_TW from './locales/zh_TW.json'

const getStoredLanguage = () => {
  try {
    const settingsString = localStorage.getItem('settings-storage')
    if (settingsString) {
      const settings = JSON.parse(settingsString)
      return settings.state?.language || 'en'
    }
  } catch (e) {
    console.error('Failed to get stored language:', e)
  }
  return 'en'
}
// eslint-disable  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y1dneVR3PT06NmI1MjY0ZDU=

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
      fr: { translation: fr },
      ar: { translation: ar },
      zh_TW: { translation: zh_TW }
    },
    lng: getStoredLanguage(), // Use stored language settings
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    // Configuration to handle missing translations
    returnEmptyString: false,
    returnNull: false,
  })

// Subscribe to language changes
useSettingsStore.subscribe((state) => {
  const currentLanguage = state.language
  if (i18n.language !== currentLanguage) {
    i18n.changeLanguage(currentLanguage)
  }
})
// @ts-expect-error  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y1dneVR3PT06NmI1MjY0ZDU=

export default i18n
