import { useEffect, useState } from "react";

export interface ResourceState<T> {
  data: T | null;
  error: boolean;
  loading: boolean;
  reload: () => void;
}

export function useResource<T>(loader: (signal: AbortSignal) => Promise<T>): ResourceState<T> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<ResourceState<T>, "reload">>({
    data: null,
    error: false,
    loading: true,
  });

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: false }));
    loader(controller.signal)
      .then((data) => setState({ data, error: false, loading: false }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setState((current) => ({ ...current, error: true, loading: false }));
      });
    return () => controller.abort();
  }, [attempt, loader]);

  return { ...state, reload: () => setAttempt((value) => value + 1) };
}
