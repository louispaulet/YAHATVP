import { NavLink } from "react-router-dom";
import { useI18n } from "../context/I18nContext";

export function NotFoundPage() {
  const { locale } = useI18n();
  return (
    <div className="mx-auto max-w-2xl px-5 py-24 text-center lg:px-8">
      <h1 className="text-4xl font-black">{locale.errors.notFound}</h1>
      <NavLink className="mt-6 inline-block rounded-full bg-ink px-5 py-3 text-sm font-bold text-white" to="/">{locale.errors.backToOverview}</NavLink>
    </div>
  );
}
