import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import ca from './locales/ca.json'
import en from './locales/en.json'
import es from './locales/es.json'
import fr from './locales/fr.json'

const supportedLanguages = ['fr', 'es', 'ca', 'en']

const savedLanguage = localStorage.getItem('language')

const browserLanguage = navigator.language
  .toLowerCase()
  .split('-')[0]

const initialLanguage =
  savedLanguage && supportedLanguages.includes(savedLanguage)
    ? savedLanguage
    : supportedLanguages.includes(browserLanguage)
      ? browserLanguage
      : 'fr'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      fr: { translation: fr },
      es: { translation: es },
      ca: { translation: ca },
      en: { translation: en },
    },

    lng: initialLanguage,
    fallbackLng: 'fr',

    interpolation: {
      escapeValue: false,
    },
  })

i18n.on('languageChanged', (language) => {
  localStorage.setItem('language', language)
  document.documentElement.lang = language
})

document.documentElement.lang = initialLanguage

export default i18n