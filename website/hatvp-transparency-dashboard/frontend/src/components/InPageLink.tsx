import type { ComponentProps } from "react";
import { Link, useLocation } from "react-router-dom";

// Keep the route and its query inside HashRouter's outer URL fragment.
export function InPageLink({ hash, ...props }: Omit<ComponentProps<typeof Link>, "to"> & { hash: string }) {
  const { pathname, search } = useLocation();
  return <Link {...props} to={{ pathname, search, hash }} />;
}
