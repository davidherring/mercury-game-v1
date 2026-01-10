import React from "react";

export interface DebugInfo {
  method?: string;
  url?: string;
  body?: unknown;
  status?: string;
  timestamp?: string;
}

export const DebugBox: React.FC<{ lastRequest?: DebugInfo; lastError?: string }> = ({ lastRequest, lastError }) => {
  const prettyBody = lastRequest?.body ? JSON.stringify(lastRequest.body, null, 2) : null;
  return (
    <div style={{ border: "1px solid #ccc", borderRadius: 4, padding: 12, fontSize: 12, color: "#333" }}>
      <div><strong>Last request:</strong> {lastRequest ? `${lastRequest.method || ""} ${lastRequest.url || ""}`.trim() : "(no requests yet)"}</div>
      {lastRequest?.timestamp && <div style={{ marginTop: 4 }}>at {lastRequest.timestamp}</div>}
      {lastRequest?.status && <div style={{ marginTop: 4 }}>status: {lastRequest.status}</div>}
      {prettyBody && (
        <pre style={{ marginTop: 8, background: "#f7f7f7", padding: 8, borderRadius: 4, whiteSpace: "pre-wrap" }}>
          {prettyBody}
        </pre>
      )}
      <div style={{ marginTop: 8 }}><strong>Last error:</strong> {lastError || "(none)"}</div>
    </div>
  );
};
