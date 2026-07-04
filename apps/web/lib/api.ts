import type { CallDetail, CallSummary, RepDetail, RepSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchReps(): Promise<RepSummary[]> {
  return getJson<RepSummary[]>("/api/reps");
}

export function fetchRep(repId: string): Promise<RepDetail> {
  return getJson<RepDetail>(`/api/reps/${repId}`);
}

export function fetchCalls(): Promise<CallSummary[]> {
  return getJson<CallSummary[]>("/api/calls");
}

export function fetchCall(callId: string): Promise<CallDetail> {
  return getJson<CallDetail>(`/api/calls/${callId}`);
}
