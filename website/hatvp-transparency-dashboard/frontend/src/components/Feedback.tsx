import { CircleAlert } from "lucide-react";
import { useI18n } from "../context/I18nContext";

export function LoadingShell({ className }: { className: string }) {
  const { locale } = useI18n();
  return <div className={`loading-shell ${className}`} role="status" aria-label={locale.loading.label} />;
}

export function SliceError({ onRetry, message }: { onRetry: () => void; message?: string }) {
  const { locale } = useI18n();
  return (
    <div className="explore-error rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950" role="alert">
      <div className="flex items-start gap-3"><CircleAlert className="mt-0.5 shrink-0 text-amber-800" size={18} strokeWidth={1.8} aria-hidden="true" /><p>{message || locale.errors.sliceLoad}</p></div>
      <button type="button" onClick={onRetry} className="mt-4 rounded-xl bg-ink px-4 py-2 text-xs font-bold text-white transition hover:bg-slate-700 focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald">
        {locale.errors.tryAgain}
      </button>
    </div>
  );
}

export function MetricSkeleton({ compact = false }: { compact?: boolean }) {
  return (
    <div className={compact ? "border-l-2 border-white/15 pl-4 first:border-l-0 first:pl-0 sm:pl-5" : "dashboard-card p-6"}>
      <LoadingShell className={compact ? "h-3 w-20 rounded-full" : "h-4 w-28 rounded-full"} />
      <LoadingShell className={compact ? "mt-4 h-9 w-28 rounded-xl" : "mt-5 h-10 w-32 rounded-xl"} />
      <LoadingShell className="mt-2 h-3 w-24 rounded-full" />
    </div>
  );
}

export function ChartSkeleton({ table = false, compact = false, label }: { table?: boolean; compact?: boolean; label?: string }) {
  return (
    <div className="space-y-4" aria-busy="true" aria-label={label}>
      <LoadingShell className={table ? "h-4 w-3/4 rounded-full" : compact ? "h-32 w-full rounded-2xl" : "h-56 w-full rounded-[1.5rem]"} />
      {table && <><LoadingShell className="h-4 w-full rounded-full" /><LoadingShell className="h-4 w-5/6 rounded-full" /><LoadingShell className="h-4 w-2/3 rounded-full" /></>}
    </div>
  );
}

export function ExploreCardSkeleton() {
  return (
    <article className="explore-card-skeleton dashboard-card min-h-[20rem] p-5" aria-busy="true">
      <div className="flex items-start justify-between"><LoadingShell className="h-8 w-12 rounded-lg" /><LoadingShell className="h-6 w-20 rounded-full" /></div>
      <LoadingShell className="mt-7 h-5 w-3/5 rounded-md" />
      <LoadingShell className="mt-3 h-4 w-4/5 rounded-md" />
      <div className="mt-6 rounded-xl bg-slate-50 p-4"><LoadingShell className="h-3 w-1/4 rounded-full" /><LoadingShell className="mt-3 h-5 w-3/4 rounded-md" /><LoadingShell className="mt-3 h-3 w-1/3 rounded-full" /></div>
      <LoadingShell className="mt-6 h-4 w-2/5 rounded-md" />
    </article>
  );
}
