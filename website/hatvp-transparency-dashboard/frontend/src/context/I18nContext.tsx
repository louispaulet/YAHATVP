import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { defaultLanguage, getLocale, type Language, type Locale } from "../config/i18n";

interface I18nContextValue {
  language: Language;
  locale: Locale;
  setLanguage: (language: Language) => void;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function readLanguagePreference(): Language {
  try {
    return window.localStorage.getItem("hatvp-language") === "fr" ? "fr" : defaultLanguage;
  } catch {
    return defaultLanguage;
  }
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(readLanguagePreference);
  const locale = getLocale(language);

  useEffect(() => {
    try {
      window.localStorage.setItem("hatvp-language", language);
    } catch {
      // Language switching still works when browser storage is unavailable.
    }
  }, [language]);

  return <I18nContext.Provider value={{ language, locale, setLanguage }}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used within the I18n provider");
  return context;
}
