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
    <header className="game-header">
      <div className="header-title">Mercury Game</div>
      <div className="header-meta">
        <div>Game ID: {gameId}</div>
        <div>Role: {confirmedRoleId}</div>
        <div>Round: {roundLabel}</div>
        <div>Phase: {phaseLabel}</div>
        {issueTitle && <div>Issue: {issueTitle}</div>}
        <div>
          Next: {nextLabel}
          {nextHint ? <span className="text-muted"> — {nextHint}</span> : null}
        </div>
      </div>
    </header>
  );
};
