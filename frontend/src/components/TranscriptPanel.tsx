import React, { useEffect, useState } from "react";
import { ApiClient } from "../api/client";
import { DebugInfo } from "./DebugBox";
import { runRequest } from "../utils/runRequest";

interface Props {
  gameId: string | null;
  api: ApiClient;
  onRequest: (req: DebugInfo) => void;
  onError: (msg: string | null) => void;
  refreshToken?: number;
}

type TranscriptRow = {
  id?: string;
  role_id?: string;
  round?: number | null;
  phase?: string | null;
  content?: string;
  [key: string]: any;
};

function displayRound(row: TranscriptRow): string | number {
  if (typeof row.round === "number") return row.round;
  const phase = row.phase || "";
  if (phase.startsWith("ROUND_1")) return 1;
  return "?";
}

export const TranscriptPanel: React.FC<Props> = ({ gameId, api, onRequest, onError, refreshToken }) => {
  const [entries, setEntries] = useState<TranscriptRow[]>([]);
  const [visibleOnly, setVisibleOnly] = useState(true);

  const fetchTranscript = async () => {
    if (!gameId) return;
    const { result, lastRequest, errorMessage } = await runRequest({
      method: "GET",
      url: `/games/${gameId}/transcript`,
      exec: () => api.getTranscript(gameId, visibleOnly ? { visibleToHuman: true } : undefined),
    });
    onRequest(lastRequest);
    if (errorMessage) {
      onError(errorMessage);
      return;
    }
    onError(null);
    if (Array.isArray(result)) {
      setEntries(result);
    } else {
      setEntries([]);
    }
  };

  useEffect(() => {
    void fetchTranscript();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId, visibleOnly, refreshToken]);

  return (
    <section style={{ padding: "8px 0" }}>
      <h3>Transcript</h3>
      {!gameId && <p>No game loaded.</p>}
      {gameId && (
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
          <button onClick={() => void fetchTranscript()} style={{ padding: "6px 10px" }}>
            Refresh transcript
          </button>
          <label style={{ fontSize: 12 }}>
            <input
              type="checkbox"
              checked={visibleOnly}
              onChange={(e) => setVisibleOnly(e.target.checked)}
              style={{ marginRight: 4 }}
            />
            Visible to human only
          </label>
        </div>
      )}
      <div style={{ maxHeight: 300, overflowY: "auto", border: "1px solid #eee", borderRadius: 4, padding: 8 }}>
        {entries.length === 0 ? (
          <p style={{ margin: 0, color: "#666" }}>No transcript entries.</p>
        ) : (
          entries.map((row, idx) => {
            const text = row.content || JSON.stringify(row);
            return (
              <div key={row.id || idx} style={{ padding: "6px 0", borderBottom: "1px solid #f0f0f0" }}>
                <div style={{ fontSize: 12, color: "#555" }}>
                  {row.role_id || "?"} — round {displayRound(row)} / {row.phase || "?"}
                </div>
                <div style={{ marginTop: 2 }}>{text}</div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
};
