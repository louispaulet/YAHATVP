import { languages } from "../config/i18n";
import { useI18n } from "../context/I18nContext";

export function LanguageSwitcher() {
  const { language, locale, setLanguage } = useI18n();

  return (
    <div className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100/70 p-1" aria-label={locale.languageSwitcher.label}>
      {languages.map((option) => (
        <button
          key={option}
          type="button"
          aria-label={locale.languageSwitcher.options[option]}
          aria-pressed={language === option}
          title={locale.languageSwitcher.options[option]}
          onClick={() => setLanguage(option)}
          className={language === option ? "rounded-full bg-white px-2.5 py-1 text-xs font-bold text-ink shadow-sm" : "rounded-full px-2.5 py-1 text-xs font-bold text-slate-500 transition hover:bg-white hover:text-ink"}
        >
          {option.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
