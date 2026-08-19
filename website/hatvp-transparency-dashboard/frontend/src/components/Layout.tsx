import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import { LanguageSwitcher } from "./LanguageSwitcher";

function navClass({ isActive }: { isActive: boolean }): string {
  return isActive
    ? "relative px-1 py-2 text-[13px] font-semibold text-ink transition after:absolute after:inset-x-1 after:-bottom-[0.35rem] after:h-0.5 after:rounded-full after:bg-emerald focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"
    : "relative px-1 py-2 text-[13px] font-semibold text-slate-500 transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald";
}

export function Layout({ children }: { children: ReactNode }) {
  const { locale } = useI18n();

  return (
    <div className="flex min-h-screen flex-col bg-canvas text-ink">
      <header className="border-b border-slate-200/80 bg-canvas/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <NavLink to="/" className="flex shrink-0 items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-2xl bg-emerald/10 text-2xl leading-none" aria-hidden="true">⚖️</span>
            <span><span className="block text-xs font-bold uppercase tracking-[0.22em] text-slate-500">HATVP</span><span className="block text-sm font-semibold">{locale.brand.name}</span></span>
          </NavLink>
          <div className="flex min-w-0 flex-wrap items-center justify-between gap-x-5 gap-y-2 lg:flex-1 lg:flex-nowrap lg:justify-end">
            <nav aria-label={locale.nav.label} className="flex min-w-0 flex-1 items-center gap-x-3 overflow-x-auto py-1 whitespace-nowrap sm:gap-x-4">
              <NavLink to="/" end className={navClass}>{locale.nav.overview}</NavLink>
              <NavLink to="/search" className={navClass}>{locale.nav.search}</NavLink>
              <NavLink to="/explore" className={navClass}>{locale.nav.explore}</NavLink>
              <NavLink to="/analysis" className={navClass}>{locale.nav.analysis}</NavLink>
              <NavLink to="/age-analysis" className={navClass}>{locale.nav.ageAnalysis}</NavLink>
              <NavLink to="/about" className={navClass}>{locale.nav.about}</NavLink>
              <NavLink to="/quality-issues" className={navClass}>{locale.nav.qualityIssues}</NavLink>
            </nav>
            <div className="shrink-0"><LanguageSwitcher /></div>
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="mt-auto border-t border-slate-200/80">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-8 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <span>{locale.footer.builtFrom}</span>
          <div className="flex flex-wrap gap-x-4 gap-y-2">
            <a className="font-semibold text-slate-700 underline decoration-lime underline-offset-4" href="https://github.com/louispaulet/YAHATVP/tree/main" target="_blank" rel="noreferrer">{locale.footer.project}</a>
            <a className="font-semibold text-slate-700 underline decoration-lime underline-offset-4" href="https://www.hatvp.fr/" target="_blank" rel="noreferrer">hatvp.fr</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
