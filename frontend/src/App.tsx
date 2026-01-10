import React, { useMemo, useState } from "react";
import { createApiClient } from "./api/client";
import { useApiBaseUrl } from "./hooks/useApiBaseUrl";
import { ErrorBanner } from "./components/ErrorBanner";
import { DebugBox, DebugInfo } from "./components/DebugBox";
import { GameSession } from "./components/GameSession";
import { ActionPanel } from "./components/ActionPanel";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { ReviewPanel } from "./components/ReviewPanel";

export const App: React.FC = () => {
  const { baseUrl, override, setOverride } = useApiBaseUrl();
  const api = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);
  const [lastRequest, setLastRequest] = useState<DebugInfo>();
  const [lastError, setLastError] = useState<string>();

  // Placeholder wiring for future use
  const handleSetBase = (val: string) => {
    setOverride(val.trim() || null);
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
        <GameSession onRequest={(req) => setLastRequest(req)} onError={(msg) => setLastError(msg || undefined)} />
        <ActionPanel />
        <TranscriptPanel />
        <ReviewPanel />
      </main>

      <section style={{ marginTop: 24 }}>
        <DebugBox lastRequest={lastRequest} lastError={lastError} />
      </section>
    </div>
  );
};
