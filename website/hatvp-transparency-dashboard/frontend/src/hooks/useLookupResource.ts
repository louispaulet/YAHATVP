import { useEffect, useState } from "react";
import type { ResourceState } from "./useResource";

type Loader<T> = (signal: AbortSignal) => Promise<T>;

export function useLookupResource<T>(key: string, loader: Loader<T>): ResourceState<T> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<T>, "reload">>({
    data: null,
    error: false,
    loading: false,
  });

  useEffect(() => {
    if (!key) {
      setState({ data: null, error: false, loading: false });
      return;
    }
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: false }));
    loader(controller.signal)
      .then((data) => setState({ data, error: false, loading: false }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setState((current) => ({ ...current, error: true, loading: false }));
      });
    return () => controller.abort();
  }, [attempt, key, loader]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}
