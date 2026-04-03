import { DashboardResponse, DashboardContext, ExplainResponse, DebugSnapshotResponse } from "../types/dashboard";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:7071/api";
const API_KEY = process.env.REACT_APP_API_KEY || "";

function endpoint(path: string): string {
  return `${API_URL}/${path}${API_KEY ? `?code=${API_KEY}` : ""}`;
}

const headers = { "Content-Type": "application/json" };

export async function fetchDashboard(payload: {
  mode?: "live" | "cached" | "blob";
  location_id?: string;
  material_group?: string;
  current_rows?: object[];
  previous_rows?: object[];
}): Promise<DashboardResponse> {
  const res = await fetch(endpoint("planning-dashboard-v2"), {
    method: "POST",
    headers,
    body: JSON.stringify({ mode: "cached", ...payload }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function fetchExplain(payload: {
  question: string;
  mode?: "live" | "cached";
  location_id?: string;
  material_group?: string;
  context?: Partial<DashboardContext>;
}): Promise<ExplainResponse> {
  const res = await fetch(endpoint("explain"), {
    method: "POST",
    headers,
    body: JSON.stringify({ mode: "cached", ...payload }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchDebugSnapshot(params?: {
  mode?: "cached" | "live" | "blob";
  location_id?: string;
  material_group?: string;
}): Promise<DebugSnapshotResponse> {
  const res = await fetch(endpoint("debug-snapshot"), {
    method: "POST",
    headers,
    body: JSON.stringify(params ?? {}),
  });
  if (!res.ok) throw new Error(`Debug snapshot error ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function triggerDailyRefresh(source: "blob" | "sharepoint" = "blob"): Promise<{
  status: string;
  lastRefreshedAt: string;
  totalRecords: number;
  changedRecordCount: number;
  planningHealth: number;
}> {
  const res = await fetch(endpoint("daily-refresh"), {
    method: "POST",
    headers,
    body: JSON.stringify({ source }),
  });
  if (!res.ok) throw new Error(`Refresh failed: ${res.status}`);
  return res.json();
}
