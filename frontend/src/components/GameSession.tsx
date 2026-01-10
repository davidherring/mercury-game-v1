import React, { useEffect, useMemo, useState } from "react";
import { createApiClient } from "../api/client";
import { useApiBaseUrl } from "../hooks/useApiBaseUrl";
import { runRequest } from "../utils/runRequest";
import { DebugInfo } from "./DebugBox";

const STORAGE_KEY = "hg_game_id";

export const GameSession: React.FC<{
  onRequest: (req: DebugInfo) => void;
  onError: (msg: string | null) => void;
}> = ({ onRequest, onError }) => {
  const { baseUrl } = useApiBaseUrl();
  const api = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);
  const [gameId, setGameId] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (gameId) {
      void fetchState(gameId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId]);

  const persistGameId = (id: string | null) => {
    setGameId(id);
    if (id) {
      localStorage.setItem(STORAGE_KEY, id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const fetchState = async (id: string) => {
    setLoading(true);
    const { result, lastRequest, errorMessage } = await runRequest({
      method: "GET",
      url: `${baseUrl}/games/${id}`,
      exec: () => api.getGame(id),
    });
    onRequest(lastRequest);
    if (errorMessage) {
      onError(errorMessage);
    } else {
      onError(null);
    }
    if (result && typeof result === "object" && "state" in result) {
      const st = (result as any).state;
      setStatus(st?.status ?? null);
    }
    setLoading(false);
  };

  const handleCreate = async () => {
    setLoading(true);
    const { result, lastRequest, errorMessage } = await runRequest({
      method: "POST",
      url: `${baseUrl}/games`,
      body: {},
      exec: () => api.createGame(),
    });
    onRequest(lastRequest);
    if (errorMessage) {
      onError(errorMessage);
      setLoading(false);
      return;
    }
    const newId = (result as any)?.game_id || (result as any)?.gameId || (result as any)?.gameID;
    if (typeof newId === "string") {
      persistGameId(newId);
      const st = (result as any)?.state;
      setStatus(st?.status ?? null);
      onError(null);
    } else {
      onError("createGame: no game_id returned");
    }
    setLoading(false);
  };

  const handleReset = () => {
    persistGameId(null);
    setStatus(null);
    onError(null);
  };

  const handleLoad = () => {
    if (gameId) {
      void fetchState(gameId);
    }
  };

  return (
    <section style={{ padding: "8px 0" }}>
      <h2>Game Session</h2>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <button onClick={handleCreate} disabled={loading} style={{ padding: "8px 12px" }}>
          Create Game
        </button>
        <button onClick={handleLoad} disabled={loading || !gameId} style={{ padding: "8px 12px" }}>
          Load Game
        </button>
        <button onClick={handleReset} style={{ padding: "8px 12px" }}>
          Reset
        </button>
        <span style={{ fontSize: 12, color: "#555" }}>API Base: {baseUrl}</span>
      </div>
      <div style={{ marginTop: 12 }}>
        <div><strong>Game ID:</strong> {gameId || "(none)"}</div>
        <div><strong>Status:</strong> {status || "(unknown)"}</div>
      </div>
    </section>
  );
};
