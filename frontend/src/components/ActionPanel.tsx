import React, { useEffect, useMemo, useState } from "react";
import { ApiClient } from "../api/client";
import { DebugInfo } from "./DebugBox";
import { runRequest } from "../utils/runRequest";

interface Props {
  gameId: string | null;
  status: string | null;
  gameState: any;
  api: ApiClient;
  onRequest: (req: DebugInfo) => void;
  onError: (msg: string | null) => void;
  onAdvanced: (state?: any) => Promise<void> | void;
  requiredAction?: string | null;
  onClearRequiredAction?: () => void;
}

const FALLBACK_ROLES = ["BRA", "CAN", "CHN", "EU", "TZA", "USA", "WCPA", "MFF", "AMAP"];
const CHAIR = "JPN";
const COUNTRY_IDS = new Set(["BRA", "CAN", "CHN", "EU", "TZA", "USA"]);
const NGO_IDS = new Set(["AMAP", "MFF", "WCPA"]);

function buildPartnerOptions(allRoles: string[], exclude: string[]) {
  const excludeSet = new Set(exclude);
  return allRoles.filter((r) => !excludeSet.has(r));
}

function sortRoles(roleIds: string[], rolesMeta?: Record<string, any>) {
  return [...roleIds].sort((a, b) => {
    const typeA =
      rolesMeta?.[a]?.type ||
      rolesMeta?.[a]?.role_type ||
      rolesMeta?.[a]?.roleType ||
      (COUNTRY_IDS.has(a) ? "country" : NGO_IDS.has(a) ? "ngo" : rolesMeta?.[a]?.role);
    const typeB =
      rolesMeta?.[b]?.type ||
      rolesMeta?.[b]?.role_type ||
      rolesMeta?.[b]?.roleType ||
      (COUNTRY_IDS.has(b) ? "country" : NGO_IDS.has(b) ? "ngo" : rolesMeta?.[b]?.role);
    const catOrder = (t?: string) => (t === "country" ? 0 : t === "ngo" ? 1 : 2);
    const catA = catOrder(typeA);
    const catB = catOrder(typeB);
    if (catA !== catB) return catA - catB;
    return a.localeCompare(b);
  });
}

export const ActionPanel: React.FC<Props> = ({
  gameId,
  status,
  gameState,
  api,
  onRequest,
  onError,
  onAdvanced,
  requiredAction,
  onClearRequiredAction,
}) => {
  const [devMode, setDevMode] = useState(false);
  const [rawEvent, setRawEvent] = useState("ROUND_1_READY");
  const [payloadText, setPayloadText] = useState("{}");
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [humanPlacement, setHumanPlacement] = useState<"first" | "random" | "skip">("random");
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [debateMessage, setDebateMessage] = useState<string>("");
  const [selectedIssueId, setSelectedIssueId] = useState<string>("");
  const [humanOpening, setHumanOpening] = useState<string>("");
  const issues: string[] = gameState?.round3?.issues || [];

  const roleOptions = useMemo(() => {
    const rolesObj =
      (gameState && typeof gameState === "object" && (gameState as any).roles) ||
      (gameState && typeof gameState === "object" && (gameState as any).available_roles);
    if (rolesObj && typeof rolesObj === "object") {
      return sortRoles(Object.keys(rolesObj), rolesObj as Record<string, any>);
    }
    return sortRoles(FALLBACK_ROLES);
  }, [gameState]);

  const humanRoleId: string | undefined =
    (gameState && (gameState as any).human_role_id) ||
    (gameState && (gameState as any).humanRoleId) ||
    undefined;
  const convo1Partner: string | undefined =
    gameState?.round2?.convo1?.partner_role || gameState?.round2?.convo1?.partner_role_id;
  const activeIssue = gameState?.round3?.active_issue;
  const closedIssues: string[] = gameState?.round3?.closed_issues || [];
  const needsHumanVote =
    status === "ISSUE_VOTE" &&
    activeIssue &&
    activeIssue.vote_order &&
    activeIssue.votes &&
    activeIssue.vote_order[activeIssue.next_voter_index] === gameState?.human_role_id;
  const isHumanDebateTurn =
    (status === "ISSUE_DEBATE_ROUND_1" || status === "ISSUE_DEBATE_ROUND_2") &&
    activeIssue &&
    Array.isArray(activeIssue.debate_queue) &&
    typeof activeIssue.debate_cursor === "number" &&
    activeIssue.debate_queue[activeIssue.debate_cursor] === humanRoleId;

  useEffect(() => {
    if (status !== "ROUND_3_SETUP") {
      return;
    }
    if (!issues || issues.length === 0) {
      setSelectedIssueId("");
      return;
    }
    const activeIssueId = activeIssue?.issue_id;
    const next =
      issues.find((id) => id !== activeIssueId && !closedIssues.includes(id)) ||
      issues[0];
    setSelectedIssueId(next);
  }, [status, issues, activeIssue?.issue_id, closedIssues.join(","), gameId]);

  const doAdvance = async (event: string, payload: Record<string, unknown>) => {
    if (!gameId) {
      onError("No game loaded");
      return;
    }
    const { lastRequest, errorMessage, result } = await runRequest({
      method: "POST",
      url: `/games/${gameId}/advance`,
      body: { event, payload },
      exec: () => api.advance(gameId, event as any, payload),
    });
    onRequest(lastRequest);
    if (errorMessage) {
      onError(errorMessage);
      return;
    }
    onError(null);
    await Promise.resolve(onAdvanced((result as any)?.state));
  };

  const handleRaw = async () => {
    if (!gameId) {
      onError("No game loaded");
      return;
    }
    let payload: any = {};
    if (payloadText.trim()) {
      try {
        payload = JSON.parse(payloadText);
      } catch {
        onError("Payload must be valid JSON");
        return;
      }
    }
    await doAdvance(rawEvent, payload);
  };

  const renderControls = () => {
    if (!gameId) return <div style={{ color: "#999" }}>No game loaded.</div>;
    switch (status) {
      case "ROLE_SELECTION":
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <label>
              Select role:
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
              >
                <option value="">-- choose --</option>
                {sortRoles(buildPartnerOptions(roleOptions, [CHAIR]), gameState?.roles).map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>
            <button
              onClick={() => doAdvance("ROLE_CONFIRMED", { human_role_id: selectedRole })}
              disabled={!selectedRole}
              style={{ padding: "8px 12px" }}
            >
              Confirm role
            </button>
          </div>
        );
      case "ROUND_1_SETUP":
        return (
          <button onClick={() => doAdvance("ROUND_1_READY", {})} style={{ padding: "8px 12px" }}>
            Round 1 Ready
          </button>
        );
      case "ROUND_1_OPENING_STATEMENTS":
      case "ROUND_1_STEP":
        // Determine if it is the human's turn based on round1.speaker_order and cursor.
        const r1 = gameState?.round1 || {};
        const r1Order: string[] = r1.speaker_order || [];
        const r1Cursor: number = typeof r1.cursor === "number" ? r1.cursor : 0;
        const r1Next = r1Order[r1Cursor];
        const isHumanOpeningTurn = !!humanRoleId && r1Next === humanRoleId;
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {isHumanOpeningTurn ? (
              <>
                <label>
                  Your opening statement:
                  <textarea
                    value={humanOpening}
                    onChange={(e) => setHumanOpening(e.target.value)}
                    rows={3}
                    style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
                  />
                </label>
                <button
                  onClick={() =>
                    doAdvance("HUMAN_OPENING_STATEMENT", { text: humanOpening }).then(() => setHumanOpening(""))
                  }
                  disabled={!humanOpening.trim()}
                  style={{ padding: "8px 12px" }}
                >
                  Submit opening
                </button>
              </>
            ) : (
              <button onClick={() => doAdvance("ROUND_1_STEP", {})} style={{ padding: "8px 12px" }}>
                Next
              </button>
            )}
          </div>
        );
      case "ROUND_2_SETUP":
        return (
          <button onClick={() => doAdvance("ROUND_2_READY", {})} style={{ padding: "8px 12px" }}>
            Round 2 Ready
          </button>
        );
      case "ROUND_2_SELECT_CONVO_1": {
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <label>
              Conversation partner:
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
              >
                <option value="">-- choose --</option>
                {sortRoles(buildPartnerOptions(roleOptions, [CHAIR, humanRoleId || ""]), gameState?.roles).map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>
            <button
              onClick={() => doAdvance("CONVO_1_SELECTED", { partner_role_id: selectedRole })}
              disabled={!selectedRole}
              style={{ padding: "8px 12px" }}
            >
              Select conversation partner
            </button>
          </div>
        );
      }
      case "ROUND_2_CONVERSATION_ACTIVE":
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <label>
              Message:
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
                style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
              />
            </label>
            <small style={{ color: "#666" }}>Backend drives turns; send when status allows.</small>
            <button
              onClick={() =>
                doAdvance("CONVO_1_MESSAGE", { content: message }).then(() => setMessage(""))
              }
              disabled={!message.trim()}
              style={{ padding: "8px 12px" }}
            >
              Send message
            </button>
          </div>
        );
      case "ROUND_2_SELECT_CONVO_2": {
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <label>
              Conversation 2 partner:
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
              >
                <option value="">-- choose --</option>
                {sortRoles(buildPartnerOptions(roleOptions, [CHAIR, humanRoleId || "", convo1Partner || ""]), gameState?.roles).map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => doAdvance("CONVO_2_SELECTED", { partner_role_id: selectedRole })}
                disabled={!selectedRole}
                style={{ padding: "8px 12px" }}
              >
                Select convo2 partner
              </button>
              <button onClick={() => doAdvance("CONVO_2_SKIPPED", {})} style={{ padding: "8px 12px" }}>
                Skip convo2
              </button>
            </div>
          </div>
        );
      }
      case "ROUND_2_WRAP_UP":
        return (
          <button onClick={() => doAdvance("ROUND_2_WRAP_READY", {})} style={{ padding: "8px 12px" }}>
            Wrap up
          </button>
        );
      case "ROUND_3_SETUP":
        return (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div>Next issue: {selectedIssueId || "(unavailable)"}</div>
            {devMode && (
              <label>
                Select issue (dev override):
                <select
                  value={selectedIssueId}
                  onChange={(e) => setSelectedIssueId(e.target.value)}
                  disabled={issues.length === 0}
                  style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
                >
                  {issues.map((id) => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              </label>
            )}
            <label>
              Human placement:
              <select
                value={humanPlacement}
                onChange={(e) => setHumanPlacement(e.target.value as any)}
                style={{ padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
              >
                <option value="first">first</option>
                <option value="random">random</option>
                <option value="skip">skip</option>
              </select>
            </label>
            <button
              onClick={() =>
                doAdvance("ROUND_3_START_ISSUE", { issue_id: selectedIssueId, human_placement: humanPlacement })
              }
              style={{ padding: "8px 12px" }}
              disabled={!selectedIssueId}
            >
              Start Issue
            </button>
          </div>
        );
      case "ISSUE_INTRO":
        return (
          <button onClick={() => doAdvance("ISSUE_INTRO_CONTINUE", {})} style={{ padding: "8px 12px" }}>
            Continue
          </button>
        );
      case "ISSUE_DEBATE_ROUND_1":
      case "ISSUE_DEBATE_ROUND_2":
      case "ISSUE_VOTE":
      case "ISSUE_RESOLUTION": {
        if (needsHumanVote) {
          const options = Array.isArray(activeIssue?.options) ? activeIssue.options : [];
          const proposedId = activeIssue?.proposed_option_id;
          const proposedLabel =
            options.find((o: any) => o.option_id === proposedId)?.label ||
            options.find((o: any) => o.option_id === proposedId)?.short_description ||
            proposedId;
          return (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: 12, color: "#555" }}>Vote on proposal {proposedId}: {proposedLabel}</div>
              <div style={{ display: "flex", gap: 12 }}>
                <label style={{ display: "flex", gap: 4, alignItems: "center" }}>
                  <input
                    type="radio"
                    name="vote-yesno"
                    value="YES"
                    checked={selectedOption === "YES"}
                    onChange={(e) => setSelectedOption(e.target.value)}
                  />
                  <span>YES</span>
                </label>
                <label style={{ display: "flex", gap: 4, alignItems: "center" }}>
                  <input
                    type="radio"
                    name="vote-yesno"
                    value="NO"
                    checked={selectedOption === "NO"}
                    onChange={(e) => setSelectedOption(e.target.value)}
                  />
                  <span>NO</span>
                </label>
              </div>
              <button
                onClick={() => doAdvance("HUMAN_VOTE", { vote: selectedOption }).then(() => setSelectedOption(""))}
                disabled={!selectedOption}
                style={{ padding: "8px 12px" }}
              >
                Submit Vote
              </button>
            </div>
          );
        }
        if (isHumanDebateTurn) {
          return (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: 12, color: "#555" }}>Human debate turn</div>
              <textarea
                value={debateMessage}
                onChange={(e) => setDebateMessage(e.target.value)}
                rows={3}
                style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
              />
              <button
                onClick={() =>
                  doAdvance("HUMAN_DEBATE_MESSAGE", { text: debateMessage }).then(() => {
                    setDebateMessage("");
                    onClearRequiredAction?.();
                  })
                }
                disabled={!debateMessage.trim()}
                style={{ padding: "8px 12px" }}
              >
                Send debate message
              </button>
              {requiredAction === "human_debate" && (
                <div style={{ fontSize: 12, color: "#b00" }}>Backend requires a human debate message before advancing.</div>
              )}
            </div>
          );
        }
        if (status === "ISSUE_RESOLUTION") {
          return (
            <button onClick={() => doAdvance("ISSUE_RESOLUTION_CONTINUE", {})} style={{ padding: "8px 12px" }}>
              Continue
            </button>
          );
        }
        return (
          <button onClick={() => doAdvance("ISSUE_DEBATE_STEP", {})} style={{ padding: "8px 12px" }}>
            Debate step
          </button>
        );
      }
      case "ISSUE_POSITION_FINALIZATION":
      case "ISSUE_PROPOSAL_SELECTION":
        return (
          <button onClick={() => doAdvance("CONTINUE", {})} style={{ padding: "8px 12px" }}>
            Continue
          </button>
        );
      default:
        return (
          <div style={{ color: "#999" }}>
            No controls implemented for this status yet.
            {devMode && (
              <div style={{ marginTop: 8 }}>
                <button onClick={() => doAdvance("CONTINUE", {})} style={{ padding: "6px 10px" }}>
                  Try CONTINUE
                </button>
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <section style={{ padding: "8px 0" }}>
      <h3>Actions</h3>
      {renderControls()}
      <div style={{ marginTop: 12 }}>
        <label style={{ fontSize: 12 }}>
          <input type="checkbox" checked={devMode} onChange={(e) => setDevMode(e.target.checked)} style={{ marginRight: 4 }} />
          Dev: show raw advance
        </label>
      </div>
      {devMode && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
          <div style={{ fontSize: 12, color: "#555" }}>Raw advance (dev)</div>
          <label>
            Event:
            <input
              type="text"
              value={rawEvent}
              onChange={(e) => setRawEvent(e.target.value)}
              style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
            />
          </label>
          <label>
            Payload (JSON):
            <textarea
              value={payloadText}
              onChange={(e) => setPayloadText(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
            />
          </label>
          <button onClick={handleRaw} disabled={!gameId} style={{ padding: "8px 12px" }}>
            POST /advance
          </button>
        </div>
      )}
    </section>
  );
};
