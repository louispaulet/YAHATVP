import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useLookupResource } from "./useLookupResource";
import { useResource } from "./useResource";

function deferred() {
  let resolve!: (value: string) => void;
  let reject!: (reason: Error) => void;
  const promise = new Promise<string>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

for (const kind of ["lookup", "dashboard"] as const) {
  describe(`${kind} request isolation`, () => {
    for (const outcome of ["success", "failure"] as const) {
      it(`ignores a stale ${outcome} after a newer request completes`, async () => {
        const old = deferred();
        const current = deferred();
        const oldLoader = () => old.promise;
        const newLoader = () => current.promise;
        const { result, rerender } = renderHook(({ loader }) => kind === "lookup"
          ? useLookupResource("query", loader) : useResource(loader), { initialProps: { loader: oldLoader } });
        rerender({ loader: newLoader });
        await act(async () => current.resolve("current result"));
        await act(async () => outcome === "success" ? old.resolve("stale result") : old.reject(new Error("late failure")));
        expect(result.current.data).toBe("current result");
        expect(result.current.error).toBe(false);
        expect(result.current.loading).toBe(false);
      });
    }
  });
}

it("does not restore a result after its query is cleared", async () => {
  const pending = deferred();
  const loader = () => pending.promise;
  const { result, rerender } = renderHook(({ query }) => useLookupResource(query, loader), { initialProps: { query: "Alice" } });
  rerender({ query: "" });
  await act(async () => pending.resolve("Alice"));
  expect(result.current.data).toBeNull();
  expect(result.current.loading).toBe(false);
});

it("does not populate a deferred resource after it is disabled", async () => {
  const pending = deferred();
  const loader = () => pending.promise;
  const { result, rerender } = renderHook(({ enabled }) => useResource(loader, { enabled }), { initialProps: { enabled: true } });
  rerender({ enabled: false });
  await act(async () => pending.resolve("disabled result"));
  expect(result.current.data).toBeNull();
  expect(result.current.loading).toBe(false);
});
