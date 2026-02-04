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
    <section className="card transcript-panel">
      <div className="section-header">
        <h2 className="section-title">Transcript</h2>
        {currentTurnRole && <span className="badge">Turn: {currentTurnRole}</span>}
      </div>
      {loading && <div>Loading transcript...</div>}
      {errorMessage && <div className="text-error">Transcript error: {errorMessage}</div>}
      <div className="transcript-list">
        {entries.length === 0 ? (
          <div>{loading ? " " : "No transcript yet."}</div>
        ) : (
          entries.map((entry, idx) => (
            <div key={entry.id || idx} className="transcript-entry">
              <div className="text-small text-muted">
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
