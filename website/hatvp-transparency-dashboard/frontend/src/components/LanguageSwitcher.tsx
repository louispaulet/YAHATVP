import { Languages } from "lucide-react";
import { languages } from "../config/i18n";
import { useI18n } from "../context/I18nContext";

export function LanguageSwitcher() {
  const { language, locale, setLanguage } = useI18n();

  return (
    <div className="language-switcher" aria-label={locale.languageSwitcher.label}>
      <Languages className="hidden size-3.5 text-slate-500 sm:block" strokeWidth={1.8} aria-hidden="true" />
      {languages.map((option) => (
        <button
          key={option}
          type="button"
          aria-label={locale.languageSwitcher.options[option]}
          aria-pressed={language === option}
          title={locale.languageSwitcher.options[option]}
          onClick={() => setLanguage(option)}
          className={language === option ? "language-switcher-option language-switcher-option--selected" : "language-switcher-option"}
        >
          {option.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
