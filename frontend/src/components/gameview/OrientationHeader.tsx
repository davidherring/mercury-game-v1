import React from "react";
import { useAuth } from "../../contexts/AuthContext";

export const OrientationHeader: React.FC<{
  gameId: string;
  confirmedRoleId: string;
  roundLabel: string;
  phaseLabel: string;
  issueTitle: string | null;
  nextLabel: string;
  nextHint?: string | null;
}> = ({ gameId, confirmedRoleId, roundLabel, phaseLabel, issueTitle, nextLabel, nextHint }) => {
  const { signOut } = useAuth();

  return (
    <header className="game-header">
      <div className="header-row">
        <div className="header-title">Mercury Game</div>
        <div className="header-actions">
          <button type="button" className="btn btn-secondary" onClick={() => void signOut()}>
            Log out
          </button>
        </div>
      </div>
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
