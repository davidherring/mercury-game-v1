import React from "react";

type TranscriptEntry = {
  id?: string;
  role_id?: string;
  phase?: string | null;
  content?: string;
};

export const TranscriptTimeline: React.FC<{
  entries: TranscriptEntry[];
  loading: boolean;
  errorMessage: string | null;
  currentTurnRole: string | null;
}> = ({ entries, loading, errorMessage, currentTurnRole }) => {
  return (
    <section style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <h2 style={{ marginTop: 0 }}>Transcript</h2>
      {currentTurnRole && (
        <div style={{ fontSize: 12, color: "#555", marginBottom: 8 }}>
          Current turn: {currentTurnRole}
        </div>
      )}
      {loading && <div>Loading transcript...</div>}
      {errorMessage && <div style={{ color: "#b00" }}>Transcript error: {errorMessage}</div>}
      <div style={{ flex: "1 1 auto", overflowY: "auto", border: "1px solid #ddd", padding: 8 }}>
        {entries.length === 0 ? (
          <div>{loading ? " " : "No transcript yet."}</div>
        ) : (
          entries.map((entry, idx) => (
            <div key={entry.id || idx} style={{ padding: "6px 0", borderBottom: "1px solid #eee" }}>
              <div style={{ fontSize: 12, color: "#555" }}>
                {entry.role_id || "?"} — {entry.phase || "?"}
              </div>
              <div>{entry.content || ""}</div>
            </div>
          ))
        )}
      </div>
    </section>
  );
};
