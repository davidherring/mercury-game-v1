import React from "react";

export const OrientationHeader: React.FC<{
  gameId: string;
  confirmedRoleId: string;
  roundLabel: string;
  phaseLabel: string;
  issueTitle: string | null;
  nextLabel: string;
  nextHint?: string | null;
}> = ({ gameId, confirmedRoleId, roundLabel, phaseLabel, issueTitle, nextLabel, nextHint }) => {
  return (
    <header style={{ borderBottom: "1px solid #ddd", padding: "12px 16px", flex: "0 0 auto" }}>
      <div style={{ fontSize: 18, fontWeight: 600 }}>Mercury Game</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginTop: 6, fontSize: 12 }}>
        <div>Game ID: {gameId}</div>
        <div>Role: {confirmedRoleId}</div>
        <div>Round: {roundLabel}</div>
        <div>Phase: {phaseLabel}</div>
        {issueTitle && <div>Issue: {issueTitle}</div>}
        <div>
          Next: {nextLabel}
          {nextHint ? <span style={{ color: "#666" }}> — {nextHint}</span> : null}
        </div>
      </div>
    </header>
  );
};
