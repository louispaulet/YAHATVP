import { useI18n } from "../context/I18nContext";

export function LoadingShell({ className }: { className: string }) {
  const { locale } = useI18n();
  return <div className={`loading-shell ${className}`} role="status" aria-label={locale.loading.label} />;
}

export function SliceError({ onRetry }: { onRetry: () => void }) {
  const { locale } = useI18n();
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
      <p>{locale.errors.sliceLoad}</p>
      <button type="button" onClick={onRetry} className="mt-3 rounded-full bg-ink px-4 py-2 text-xs font-bold text-white transition hover:bg-slate-700">
        {locale.errors.tryAgain}
      </button>
    </div>
  );
}

export function MetricSkeleton() {
  return (
    <article className="dashboard-card p-6">
      <LoadingShell className="h-4 w-28 rounded-full" />
      <LoadingShell className="mt-5 h-10 w-32 rounded-xl" />
      <LoadingShell className="mt-3 h-3 w-24 rounded-full" />
    </article>
  );
}

export function ChartSkeleton({ table = false }: { table?: boolean }) {
  return (
    <div className="space-y-4" aria-busy="true">
      <LoadingShell className={table ? "h-4 w-3/4 rounded-full" : "h-56 w-full rounded-[1.5rem]"} />
      {table && <><LoadingShell className="h-4 w-full rounded-full" /><LoadingShell className="h-4 w-5/6 rounded-full" /><LoadingShell className="h-4 w-2/3 rounded-full" /></>}
    </div>
  );
}
