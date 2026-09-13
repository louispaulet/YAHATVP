import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export function useRouteFocus() {
  const { pathname, hash, key } = useLocation();
  useEffect(() => {
    if (!hash) {
      document.getElementById("main-content")?.focus({ preventScroll: true });
      return;
    }

    let targetId: string;
    try {
      targetId = decodeURIComponent(hash.slice(1));
    } catch {
      return;
    }
    function focusTarget() {
      const target = document.getElementById(targetId);
      if (!target) return false;
      if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      target.scrollIntoView({ block: "start" });
      return true;
    }
    if (focusTarget()) return;

    // Linked declaration sections may arrive after the initial route render.
    const observer = new MutationObserver(() => {
      if (focusTarget()) observer.disconnect();
    });
    observer.observe(document.getElementById("main-content") ?? document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [pathname, hash, key]);
}
