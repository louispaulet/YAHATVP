import type { ReactNode } from "react";

interface DisclosureProps {
  summary: string;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  open?: boolean;
}

/** A small, keyboard-native disclosure for supplementary reading. */
export function Disclosure({ summary, children, className = "", contentClassName = "", open }: DisclosureProps) {
  return (
    <details className={`rounded-2xl border border-slate-200 bg-surface-subtle ${className}`} open={open}>
      <summary className="cursor-pointer rounded-2xl px-4 py-3 text-sm font-bold text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald">
        {summary}
      </summary>
      <div className={`px-4 pb-4 text-sm leading-6 text-slate-600 ${contentClassName}`}>{children}</div>
    </details>
  );
}
