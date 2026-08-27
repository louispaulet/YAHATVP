import { useEffect, useState } from "react";

export interface ResourceState<T> {
  data: T | null;
  error: boolean;
  loading: boolean;
  reload: () => void;
}

export function useResource<T>(loader: (signal: AbortSignal) => Promise<T>, options: { enabled?: boolean } = {}): ResourceState<T> {
  const enabled = options.enabled ?? true;
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<T>, "reload">>({
    data: null,
    error: false,
    loading: enabled,
  });

  useEffect(() => {
    if (!enabled) {
      setState((current) => ({ ...current, loading: false }));
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
  }, [attempt, enabled, loader]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}
