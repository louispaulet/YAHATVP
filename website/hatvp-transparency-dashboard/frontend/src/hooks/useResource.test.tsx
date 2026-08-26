import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useResource } from "./useResource";

describe("useResource", () => {
  it("keeps deferred resources idle until enabled, then loads them", async () => {
    const loader = vi.fn().mockResolvedValue({ value: "loaded" });
    const { result, rerender } = renderHook(({ enabled }) => useResource(loader, { enabled }), { initialProps: { enabled: false } });

    expect(result.current.loading).toBe(false);
    expect(loader).not.toHaveBeenCalled();
    rerender({ enabled: true });
    await waitFor(() => expect(result.current.data).toEqual({ value: "loaded" }));
    expect(loader).toHaveBeenCalledTimes(1);
  });
});
