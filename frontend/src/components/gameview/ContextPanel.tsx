import React from "react";

type ContextRow = {
  label: string;
  value: string;
};

export const ContextPanel: React.FC<{
  gameState: any;
  loading: boolean;
  errorMessage: string | null;
  nextActionLabel?: string | null;
}> = ({ gameState, loading, errorMessage, nextActionLabel }) => {
  const status = typeof gameState?.status === "string" ? gameState.status : null;
  const roundLabel = deriveRoundLabel(status);
  const turnOrder = buildTurnOrder(gameState, status);
  const activeIssue = gameState?.round3?.active_issue;
  const issueTitle =
    activeIssue && typeof activeIssue.issue_title === "string" ? activeIssue.issue_title : null;
  const issueFraming =
    activeIssue && typeof activeIssue.ui_prompt === "string" ? activeIssue.ui_prompt : null;
  const issueOptions = Array.isArray(activeIssue?.options) ? activeIssue.options : [];

  return (
    <section className="panel-stack">
      <div className="card">
        <div className="section-header">
          <h2 className="section-title">Structure</h2>
        </div>
        {loading && <div className="text-small text-muted">Loading state...</div>}
        {errorMessage && <div className="text-small text-error">State error: {errorMessage}</div>}
        <div className="info-list">
          <div className="info-row">
            <span className="text-small text-muted">Round</span>
            <span>{roundLabel}</span>
          </div>
          <div className="info-row">
            <span className="text-small text-muted">Phase</span>
            <span>{status || "(unknown)"}</span>
          </div>
          {nextActionLabel && (
            <div className="info-row">
              <span className="text-small text-muted">Next action</span>
              <span>{nextActionLabel}</span>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h2 className="section-title">Turn Order</h2>
        </div>
        {turnOrder.length === 0 ? (
          <div className="text-small text-muted">Turn order unavailable for this step.</div>
        ) : (
          <div className="turn-list">
            {turnOrder.map((item, idx) => (
              <div key={`${item.roleId}-${idx}`} className="turn-item">
                <span className={`turn-icon is-${item.state}`}>
                  {item.state === "done" ? "✓" : item.state === "current" ? "→" : " "}
                </span>
                <span>{item.roleId}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {issueTitle || issueFraming || issueOptions.length > 0 ? (
        <div className="card">
          <div className="section-header">
            <h2 className="section-title">Active Issue</h2>
          </div>
          {issueTitle && <div className="issue-title">{issueTitle}</div>}
          {issueFraming && <div className="issue-framing">{issueFraming}</div>}
          {issueOptions.length > 0 && (
            <div className="issue-options">
              {issueOptions.map((opt: any, idx: number) => {
                const label = typeof opt?.label === "string" ? opt.label : null;
                const optionId = typeof opt?.option_id === "string" ? opt.option_id : null;
                const description =
                  typeof opt?.description === "string" ? opt.description : null;
                const heading = optionId && label ? `${optionId}. ${label}` : optionId || label || "Option";
                return (
                  <div key={`${optionId || label || "opt"}-${idx}`} className="issue-option">
                    <div className="issue-option-title">{heading}</div>
                    {description && <div className="issue-option-desc">{description}</div>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : null}
    </section>
  );
};

function deriveRoundLabel(status: string | null): string {
  if (!status) return "(unknown)";
  if (status.startsWith("ROUND_1")) return "1";
  if (status.startsWith("ROUND_2")) return "2";
  if (status.startsWith("ROUND_3") || status.startsWith("ISSUE_")) return "3";
  return "(unknown)";
}

type TurnItem = { roleId: string; state: "done" | "current" | "upcoming" };

function buildTurnOrder(state: any, status: string | null): TurnItem[] {
  if (!status) return [];
  if (status.startsWith("ROUND_1")) {
    const order = Array.isArray(state?.round1?.speaker_order) ? state.round1.speaker_order : [];
    const cursor = typeof state?.round1?.cursor === "number" ? state.round1.cursor : null;
    return order.map((roleId: string, idx: number) => ({
      roleId,
      state: cursor === null ? "upcoming" : idx < cursor ? "done" : idx === cursor ? "current" : "upcoming",
    }));
  }
  if (status === "ISSUE_DEBATE_ROUND_1" || status === "ISSUE_DEBATE_ROUND_2") {
    const queue = Array.isArray(state?.round3?.active_issue?.debate_queue)
      ? state.round3.active_issue.debate_queue
      : [];
    const cursor = typeof state?.round3?.active_issue?.debate_cursor === "number"
      ? state.round3.active_issue.debate_cursor
      : null;
    return queue.map((roleId: string, idx: number) => ({
      roleId,
      state: cursor === null ? "upcoming" : idx < cursor ? "done" : idx === cursor ? "current" : "upcoming",
    }));
  }
  if (status === "ISSUE_VOTE") {
    const order = Array.isArray(state?.round3?.active_issue?.vote_order)
      ? state.round3.active_issue.vote_order
      : [];
    const cursor = typeof state?.round3?.active_issue?.next_voter_index === "number"
      ? state.round3.active_issue.next_voter_index
      : null;
    return order.map((roleId: string, idx: number) => ({
      roleId,
      state: cursor === null ? "upcoming" : idx < cursor ? "done" : idx === cursor ? "current" : "upcoming",
    }));
  }
  return [];
}
