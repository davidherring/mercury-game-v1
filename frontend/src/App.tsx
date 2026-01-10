import React, { useMemo, useState } from "react";
import { createApiClient } from "./api/client";
import { useApiBaseUrl } from "./hooks/useApiBaseUrl";
import { ErrorBanner } from "./components/ErrorBanner";
import { DebugBox, DebugInfo } from "./components/DebugBox";
import { GameSession } from "./components/GameSession";
import { ActionPanel } from "./components/ActionPanel";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { ReviewPanel } from "./components/ReviewPanel";
import { runRequest } from "./utils/runRequest";

const REQUIRED_ACTION_STORAGE_PREFIX = "mercury:requiredAction:";

export const App: React.FC = () => {
  const { baseUrl, override, setOverride } = useApiBaseUrl();
  const api = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);
  const [lastRequest, setLastRequest] = useState<DebugInfo>();
  const [lastError, setLastError] = useState<string>();
  const [gameId, setGameId] = useState<string | null>(null);
  const [stateObj, setStateObj] = useState<any>(null);
  const [transcriptRefreshToken, setTranscriptRefreshToken] = useState(0);
  const [refreshStateFn, setRefreshStateFn] = useState<(() => Promise<void>) | null>(null);
  const [reviewPayload, setReviewPayload] = useState<any>(null);
  const [loadingReview, setLoadingReview] = useState(false);
  const [requiredAction, setRequiredAction] = useState<string | null>(null);

  const refreshAll = async () => {
    if (refreshStateFn) {
      await refreshStateFn();
    }
    setTranscriptRefreshToken((t) => t + 1);
  };

  const fetchReview = async () => {
    if (!gameId) return;
    setLoadingReview(true);
    const { result, lastRequest, errorMessage } = await runRequest({
      method: "GET",
      url: `/games/${gameId}/review`,
      exec: () => api.getReview(gameId),
    });
    setLastRequest(lastRequest);
    if (errorMessage) {
      setLastError(errorMessage);
    } else {
      setLastError(undefined);
    }
    if (result) {
      setReviewPayload(result);
    }
    setLoadingReview(false);
  };

  // Placeholder wiring for future use
  const handleSetBase = (val: string) => {
    setOverride(val.trim() || null);
  };

  const loadRequiredAction = (gid: string | null) => {
    if (!gid) {
      setRequiredAction(null);
      return;
    }
    const stored = localStorage.getItem(`${REQUIRED_ACTION_STORAGE_PREFIX}${gid}`);
    setRequiredAction(stored || null);
  };

  const persistRequiredAction = (gid: string | null, action: string | null) => {
    if (!gid) {
      setRequiredAction(action);
      return;
    }
    const key = `${REQUIRED_ACTION_STORAGE_PREFIX}${gid}`;
    if (action) {
      localStorage.setItem(key, action);
    } else {
      localStorage.removeItem(key);
    }
    setRequiredAction(action);
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "16px", fontFamily: "Inter, system-ui, sans-serif" }}>
      <header style={{ marginBottom: 16 }}>
        <h1>Mercury Game (Frontend P0)</h1>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, maxWidth: 360 }}>
          API Base URL (env default: {import.meta.env.VITE_API_BASE_URL || "/api"})
          <input
            type="text"
            value={override ?? ""}
            placeholder={baseUrl}
            onChange={(e) => handleSetBase(e.target.value)}
            style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
          />
        </label>
      </header>

      <ErrorBanner message={lastError} onClear={() => setLastError(null)} />

      <main>
        <GameSession
          onRequest={(req) => setLastRequest(req)}
          onError={(msg) => {
            if (msg && msg.includes("requires HUMAN_DEBATE_MESSAGE")) {
              persistRequiredAction(gameId, "human_debate");
            }
            setLastError(msg || undefined);
          }}
          onRefreshRequested={refreshAll}
          setGameIdExternal={(id) => {
            setGameId(id);
            loadRequiredAction(id);
          }}
          onStateChange={(st) => setStateObj(st)}
          registerRefresh={(fn) => setRefreshStateFn(() => fn)}
        />
        <ActionPanel
          gameId={gameId}
          status={stateObj?.status || null}
          gameState={stateObj}
          api={api}
          onRequest={(req) => setLastRequest(req)}
          onError={(msg) => {
            if (msg && msg.includes("requires HUMAN_DEBATE_MESSAGE")) {
              persistRequiredAction(gameId, "human_debate");
            }
            setLastError(msg || undefined);
          }}
          onAdvanced={() => refreshAll()}
          requiredAction={requiredAction}
          onClearRequiredAction={() => persistRequiredAction(gameId, null)}
        />
        <TranscriptPanel
          gameId={gameId}
          api={api}
          onRequest={(req) => setLastRequest(req)}
          onError={(msg) => setLastError(msg || undefined)}
          refreshToken={transcriptRefreshToken}
        />
        <ReviewPanel />
        <div style={{ marginTop: 12 }}>
          {stateObj?.status === "REVIEW" && (
            <button onClick={() => void fetchReview()} disabled={loadingReview} style={{ padding: "8px 12px" }}>
              {loadingReview ? "Loading review..." : "Load Review"}
            </button>
          )}
        </div>
        <ReviewPanel review={reviewPayload} />
      </main>

      <section style={{ marginTop: 24 }}>
        <DebugBox lastRequest={lastRequest} lastError={lastError} />
      </section>
    </div>
  );
};
