const defaultBase = import.meta.env.VITE_API_BASE_URL || "/api";

export type AdvanceEvent =
  | "ROLE_CONFIRMED"
  | "ROUND_1_READY"
  | "ROUND_1_STEP"
  | "ROUND_2_READY"
  | "CONVO_1_SELECTED"
  | "CONVO_1_MESSAGE"
  | "CONVO_2_SELECTED"
  | "CONVO_2_MESSAGE"
  | "CONVO_2_SKIPPED"
  | "ROUND_2_WRAP_READY"
  | "ROUND_3_START_ISSUE"
  | "ISSUE_INTRO_CONTINUE"
  | "ISSUE_DEBATE_STEP"
  | "HUMAN_VOTE"
  | "ISSUE_RESOLUTION_CONTINUE";

export interface ApiClientConfig {
  baseUrl?: string;
}

async function requestJson(path: string, options: RequestInit = {}, baseUrl = defaultBase) {
  const res = await fetch(`${baseUrl}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return text ? JSON.parse(text) : null;
}

export function createApiClient(config: ApiClientConfig = {}) {
  const baseUrl = config.baseUrl || defaultBase;

  return {
    health: () => requestJson("/health", {}, baseUrl),
    createGame: () => requestJson("/games", { method: "POST", body: "{}" }, baseUrl),
    getGame: (gameId: string) => requestJson(`/games/${gameId}`, {}, baseUrl),
    advance: (gameId: string, event: AdvanceEvent, payload: Record<string, unknown> = {}) =>
      requestJson(`/games/${gameId}/advance`, {
        method: "POST",
        body: JSON.stringify({ event, payload }),
      }, baseUrl),
    getTranscript: (gameId: string, opts?: { visibleToHuman?: boolean }) => {
      const params = opts && opts.visibleToHuman !== undefined ? `?visible_to_human=${opts.visibleToHuman}` : "";
      return requestJson(`/games/${gameId}/transcript${params}`, {}, baseUrl);
    },
    getReview: (gameId: string) => requestJson(`/games/${gameId}/review`, {}, baseUrl),
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
