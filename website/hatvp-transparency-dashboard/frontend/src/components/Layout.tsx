import type { ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { useI18n } from "../context/I18nContext";
import { LanguageSwitcher } from "./LanguageSwitcher";

type SectionKey = "explore" | "declarations" | "data";
type ChildLink = { to: string; label: string; end?: boolean };

function sectionForPath(pathname: string): SectionKey | null {
  if (pathname === "/" || pathname.startsWith("/explore") || pathname.startsWith("/analysis")) return "explore";
  if (pathname.startsWith("/search") || pathname.startsWith("/age-analysis") || pathname.startsWith("/declarations/")) return "declarations";
  if (pathname.startsWith("/about") || pathname.startsWith("/quality-issues")) return "data";
  return null;
}

function parentClass(active: boolean): string {
  return active
    ? "relative px-3 py-2 text-[13px] font-bold text-ink transition after:absolute after:inset-x-3 after:-bottom-[0.35rem] after:h-0.5 after:rounded-full after:bg-emerald focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"
    : "relative px-3 py-2 text-[13px] font-semibold text-slate-500 transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald";
}

function childClass({ isActive }: { isActive: boolean }): string {
  return isActive
    ? "relative px-1 py-1.5 text-xs font-bold text-emerald transition after:absolute after:inset-x-1 after:-bottom-0.5 after:h-0.5 after:rounded-full after:bg-emerald focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald"
    : "relative px-1 py-1.5 text-xs font-semibold text-slate-500 transition hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald";
}

export function Layout({ children }: { children: ReactNode }) {
  const { locale } = useI18n();
  const { pathname } = useLocation();
  const currentSection = sectionForPath(pathname);
  const sections = [
    { key: "explore" as const, to: "/", label: locale.nav.explore },
    { key: "declarations" as const, to: "/search", label: locale.nav.declarations },
    { key: "data" as const, to: "/about", label: locale.nav.data },
  ];
  const childrenBySection: Record<SectionKey, ChildLink[]> = {
    explore: [
      { to: "/", label: locale.nav.snapshot, end: true },
      { to: "/explore", label: locale.nav.highlights },
      { to: "/analysis", label: locale.nav.populationPay },
    ],
    declarations: [
      { to: "/search", label: locale.nav.search },
      { to: "/age-analysis", label: locale.nav.profiles },
    ],
    data: [
      { to: "/about", label: locale.nav.sources, end: true },
      { to: "/quality-issues", label: locale.nav.quality },
    ],
  };

  return (
    <div className="flex min-h-screen flex-col bg-canvas text-ink">
      <header className="border-b border-slate-200/80 bg-canvas/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-4 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <Link to="/" className="flex shrink-0 items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-2xl bg-emerald/10 text-2xl leading-none" aria-hidden="true">⚖️</span>
            <span><span className="block text-xs font-bold uppercase tracking-[0.22em] text-slate-500">HATVP</span><span className="block text-sm font-semibold">{locale.brand.name}</span></span>
          </Link>
          <div className="flex min-w-0 flex-wrap items-center justify-between gap-x-5 gap-y-2 lg:flex-1 lg:flex-nowrap lg:justify-end">
            <nav aria-label={locale.nav.label} className="flex min-w-0 flex-1 items-center gap-x-1 overflow-x-auto py-1 whitespace-nowrap sm:gap-x-2">
              {sections.map((section) => <Link key={section.key} to={section.to} aria-current={currentSection === section.key ? "page" : undefined} className={parentClass(currentSection === section.key)}>{section.label}</Link>)}
            </nav>
            <div className="shrink-0"><LanguageSwitcher /></div>
          </div>
        </div>
        {currentSection && <div className="border-t border-slate-200/60"><nav aria-label={locale.nav.sectionLabel} className="mx-auto flex max-w-7xl gap-x-5 overflow-x-auto px-5 py-2 whitespace-nowrap lg:px-8">{childrenBySection[currentSection].map((child) => <NavLink key={child.to} to={child.to} end={child.end} className={childClass}>{child.label}</NavLink>)}</nav></div>}
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
