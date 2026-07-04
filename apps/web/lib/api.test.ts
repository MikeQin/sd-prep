import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchReps } from "./api";

describe("fetchReps", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns parsed rep list on success", async () => {
    const mockReps = [
      { id: "rep-01", name: "Jordan Blake", vertical: "home_services", call_count: 4, average_score: 82.5 },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockReps,
    }) as unknown as typeof fetch;

    const result = await fetchReps();

    expect(result).toEqual(mockReps);
    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/api/reps", {
      next: { revalidate: 60 },
    });
  });

  it("throws when the response is not ok", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as unknown as typeof fetch;

    await expect(fetchReps()).rejects.toThrow("Request to /api/reps failed with status 500");
  });

  it("falls back to localhost when the base URL env var is an empty string", async () => {
    vi.resetModules();
    process.env.NEXT_PUBLIC_API_BASE_URL = "";
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [] }) as unknown as typeof fetch;

    const { fetchReps: fetchRepsWithEmptyEnv } = await import("./api");
    await fetchRepsWithEmptyEnv();

    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/api/reps", expect.anything());
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
  });
});
