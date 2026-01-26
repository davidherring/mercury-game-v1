import React from "react";

type ContextRow = {
  label: string;
  value: string;
};

export const ContextPanel: React.FC<{
  gameState: any;
  loading: boolean;
  errorMessage: string | null;
}> = ({ gameState, loading, errorMessage }) => {
  const rows: ContextRow[] = [];
  const round1 = gameState?.round1;
  if (Array.isArray(round1?.speaker_order)) {
    rows.push({ label: "Round 1 speaker order", value: round1.speaker_order.join(", ") });
  }
  if (typeof round1?.cursor === "number") {
    rows.push({ label: "Round 1 cursor", value: String(round1.cursor) });
  }
  const round2 = gameState?.round2;
  if (Array.isArray(round2?.human_conversations)) {
    rows.push({ label: "Round 2 conversations", value: String(round2.human_conversations.length) });
  }
  const activeIssue = gameState?.round3?.active_issue;
  if (activeIssue && typeof activeIssue === "object") {
    if (typeof activeIssue.issue_id === "string") {
      rows.push({ label: "Active issue ID", value: activeIssue.issue_id });
    }
    if (typeof activeIssue.round_index === "number") {
      rows.push({ label: "Issue debate round", value: String(activeIssue.round_index) });
    }
    if (Array.isArray(activeIssue.debate_queue)) {
      rows.push({ label: "Debate queue", value: activeIssue.debate_queue.join(", ") });
    }
    if (typeof activeIssue.debate_cursor === "number") {
      rows.push({ label: "Debate cursor", value: String(activeIssue.debate_cursor) });
    }
  }

  return (
    <section>
      <h2 style={{ marginTop: 0 }}>Context</h2>
      {loading && <div>Loading state...</div>}
      {errorMessage && <div style={{ color: "#b00" }}>State error: {errorMessage}</div>}
      {rows.length === 0 ? (
        <div>Context will render here when available.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {rows.map((row) => (
            <div key={row.label}>
              <div style={{ fontSize: 12, color: "#555" }}>{row.label}</div>
              <div>{row.value}</div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
