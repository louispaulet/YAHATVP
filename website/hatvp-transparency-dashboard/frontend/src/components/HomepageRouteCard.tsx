import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

type RouteTone = "emerald" | "sky" | "violet";

const toneClasses: Record<RouteTone, string> = {
  emerald: "border-emerald/20 bg-emerald/5 hover:border-emerald/45",
  sky: "border-sky/35 bg-sky/10 hover:border-sky/60",
  violet: "border-violet/35 bg-violet/10 hover:border-violet/60",
};

export function HomepageRouteCard({ to, eyebrow, title, description, action, tone }: { to: string; eyebrow: string; title: string; description: string; action: string; tone: RouteTone }) {
  return (
    <Link to={to} className={`group flex min-h-44 flex-col justify-between rounded-[1.35rem] border p-5 transition duration-200 hover:-translate-y-0.5 hover:shadow-card-raised focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-emerald sm:p-6 ${toneClasses[tone]}`}>
      <div>
        <p className="text-[10px] font-bold uppercase tracking-[0.17em] text-emerald">{eyebrow}</p>
        <h3 className="mt-3 text-xl font-bold leading-tight tracking-tight text-ink">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
      </div>
      <span className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-ink">
        {action}
        <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" strokeWidth={2.2} aria-hidden="true" />
      </span>
    </Link>
  );
}
