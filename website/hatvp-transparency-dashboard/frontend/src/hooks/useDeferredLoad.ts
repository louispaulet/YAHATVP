import { useEffect, useRef, useState } from "react";

interface DeferredLoadState {
  ready: boolean;
  sentinelRef: (node: HTMLDivElement | null) => void;
}

export function useDeferredLoad(rootMargin = "0px 0px 600px 0px"): DeferredLoadState {
  const nodeRef = useRef<HTMLDivElement | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const [ready, setReady] = useState(false);

  const sentinelRef = (node: HTMLDivElement | null) => {
    nodeRef.current = node;
  };

  useEffect(() => {
    if (ready || !nodeRef.current) return;

    if (typeof IntersectionObserver === "undefined") {
      const timeout = window.setTimeout(() => setReady(true), 250);
      return () => window.clearTimeout(timeout);
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        setReady(true);
        observer.disconnect();
      },
      { rootMargin, threshold: 0 },
    );
    observerRef.current = observer;
    observer.observe(nodeRef.current);
    return () => {
      observer.disconnect();
      observerRef.current = null;
    };
  }, [ready, rootMargin]);

  return { ready, sentinelRef };
}
