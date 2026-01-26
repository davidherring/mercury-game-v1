import React, { useCallback, useEffect, useMemo, useState } from "react";
import { AdvanceEvent, createApiClient } from "../api/client";
import { OrientationHeader } from "../components/gameview/OrientationHeader";
import { ContextPanel } from "../components/gameview/ContextPanel";
import { ActionBar } from "../components/gameview/ActionBar";
import { TranscriptTimeline } from "../components/gameview/TranscriptTimeline";
import { useApiBaseUrl } from "../hooks/useApiBaseUrl";

type TranscriptEntry = {
  id?: string;
  role_id?: string;
  phase?: string | null;
  content?: string;
};

export const GameViewPage: React.FC<{ gameId: string; confirmedRoleId: string }> = ({ gameId, confirmedRoleId }) => {
  const { baseUrl } = useApiBaseUrl();
  const api = useMemo(() => createApiClient({ baseUrl }), [baseUrl]);
  const [gameState, setGameState] = useState<any>(null);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [stateError, setStateError] = useState<string | null>(null);
  const [transcriptError, setTranscriptError] = useState<string | null>(null);
  const [advanceError, setAdvanceError] = useState<string | null>(null);
  const [messageError, setMessageError] = useState<string | null>(null);
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [loadingState, setLoadingState] = useState(false);
  const [loadingTranscript, setLoadingTranscript] = useState(false);
  const [advancing, setAdvancing] = useState(false);
  const [messageText, setMessageText] = useState("");
  const [selectionValue, setSelectionValue] = useState("");
  const [skipSecondConvo, setSkipSecondConvo] = useState(false);
  const [selectedIssueId, setSelectedIssueId] = useState("");
  const [humanPlacement, setHumanPlacement] = useState<"first" | "random" | "skip">("random");

  const fetchState = useCallback(async () => {
    setLoadingState(true);
    try {
      const result = await api.getGame(gameId);
      const nextState = (result as any)?.state ?? null;
      setGameState(nextState);
      setStateError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setStateError(message);
    } finally {
      setLoadingState(false);
    }
  }, [api, gameId]);

  const fetchTranscript = useCallback(async () => {
    setLoadingTranscript(true);
    try {
      const result = await api.getTranscript(gameId, { visibleToHuman: true });
      setTranscript(Array.isArray(result) ? result : []);
      setTranscriptError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setTranscriptError(message);
    } finally {
      setLoadingTranscript(false);
    }
  }, [api, gameId]);

  useEffect(() => {
    void fetchState();
  }, [fetchState]);

  useEffect(() => {
    void fetchTranscript();
  }, [fetchTranscript]);

  const status: string | null = gameState?.status ?? null;
  const roundLabel = deriveRoundLabel(status);
  const issueTitle = deriveIssueTitle(gameState, roundLabel);
  const nextInfo = deriveNextIndicator(gameState, confirmedRoleId);
  const currentTurnRole = deriveCurrentTurnRole(gameState);
  const action = deriveActionConfig(gameState, confirmedRoleId);
  const actionKey = `${action.mode}:${action.event || action.round3?.event || "none"}`;

  useEffect(() => {
    setMessageText("");
    setMessageError(null);
    setAdvanceError(null);
    setSelectionValue("");
    setSkipSecondConvo(false);
    setSelectionError(null);
    setSelectedIssueId(action.round3?.defaultIssueId || "");
    setHumanPlacement("random");
  }, [actionKey]);

  const handleAdvance = useCallback(async () => {
    if (!action.enabled || !action.event) return;
    setAdvanceError(null);
    setAdvancing(true);
    try {
      await api.advance(gameId, action.event, action.payload || {});
      await fetchState();
      await fetchTranscript();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setAdvanceError(message || "Could not advance game");
    } finally {
      setAdvancing(false);
    }
  }, [action, api, fetchState, fetchTranscript, gameId]);

  const handleSubmitMessage = useCallback(async () => {
    if (!action.enabled || !action.event || !action.message) return;
    const trimmed = messageText.trim();
    if (!trimmed) return;
    setMessageError(null);
    setAdvancing(true);
    try {
      await api.advance(gameId, action.event, { [action.message.payloadKey]: trimmed });
      await fetchState();
      await fetchTranscript();
      setMessageText("");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setMessageError(message || "Could not submit message");
    } finally {
      setAdvancing(false);
    }
  }, [action, api, fetchState, fetchTranscript, gameId, messageText]);

  const handleSecondaryAction = useCallback(async () => {
    if (!action.message?.secondaryEvent) return;
    setMessageError(null);
    setAdvancing(true);
    try {
      await api.advance(gameId, action.message.secondaryEvent, {});
      await fetchState();
      await fetchTranscript();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setMessageError(message || "Could not end conversation");
    } finally {
      setAdvancing(false);
    }
  }, [action, api, fetchState, fetchTranscript, gameId]);

  const handleSelectionSubmit = useCallback(async () => {
    if (!action.enabled || !action.event) return;
    if (!action.selection) return;
    const shouldSkip = action.selection.allowSkip && skipSecondConvo;
    if (!shouldSkip && !selectionValue) return;
    setSelectionError(null);
    setAdvancing(true);
    try {
      if (shouldSkip && action.selection.skipEvent) {
        await api.advance(gameId, action.selection.skipEvent, {});
      } else {
        const payloadKey = action.selection.payloadKey || "partner_role_id";
        await api.advance(gameId, action.selection.selectEvent, { [payloadKey]: selectionValue });
      }
      await fetchState();
      await fetchTranscript();
      setSelectionValue("");
      setSkipSecondConvo(false);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setSelectionError(message || "Could not select conversation");
    } finally {
      setAdvancing(false);
    }
  }, [action, api, fetchState, fetchTranscript, gameId, selectionValue, skipSecondConvo]);

  const handleRound3Start = useCallback(async () => {
    if (!action.round3) return;
    if (!selectedIssueId) return;
    setSelectionError(null);
    setAdvancing(true);
    try {
      await api.advance(gameId, action.round3.event, {
        issue_id: selectedIssueId,
        human_placement: humanPlacement,
      });
      await fetchState();
      await fetchTranscript();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setSelectionError(message || "Could not start Round 3");
    } finally {
      setAdvancing(false);
    }
  }, [action, api, fetchState, fetchTranscript, gameId, selectedIssueId, humanPlacement]);

  const isActionEnabled =
    action.mode === "message"
      ? action.enabled && messageText.trim().length > 0
      : action.mode === "selection"
        ? action.enabled && (skipSecondConvo || selectionValue.length > 0)
        : action.mode === "round3_setup"
          ? action.enabled && selectedIssueId.length > 0
          : action.enabled;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <OrientationHeader
        gameId={gameId}
        confirmedRoleId={confirmedRoleId}
        roundLabel={roundLabel}
        phaseLabel={status || "(unknown)"}
        issueTitle={issueTitle}
        nextLabel={nextInfo.label}
        nextHint={nextInfo.hint}
      />
      <div style={{ display: "flex", flex: "1 1 auto", overflow: "hidden" }}>
        <div style={{ flex: 1, padding: 16, overflow: "hidden", display: "flex", flexDirection: "column" }}>
          <TranscriptTimeline
            entries={transcript}
            loading={loadingTranscript}
            errorMessage={transcriptError}
            currentTurnRole={currentTurnRole}
          />
        </div>
        <div style={{ width: 360, padding: 16, borderLeft: "1px solid #ddd", overflowY: "auto" }}>
          <ContextPanel gameState={gameState} loading={loadingState} errorMessage={stateError} />
        </div>
      </div>
      <ActionBar
        label={action.label}
        enabled={isActionEnabled}
        disabledReason={
          action.mode === "message" && !messageText.trim()
            ? "Message required."
            : action.mode === "selection" && !skipSecondConvo && !selectionValue
              ? "Selection required."
              : action.mode === "round3_setup" && !selectedIssueId
                ? "Issue selection required."
              : action.disabledReason
        }
        onAction={
          action.mode === "message"
            ? handleSubmitMessage
            : action.mode === "selection"
              ? handleSelectionSubmit
              : action.mode === "round3_setup"
                ? handleRound3Start
                : handleAdvance
        }
        loading={advancing}
        errorMessage={
          action.mode === "message"
            ? messageError
            : action.mode === "selection" || action.mode === "round3_setup"
              ? selectionError
              : advanceError
        }
        mode={action.mode}
        messageValue={messageText}
        messagePlaceholder={action.mode === "message" ? action.placeholder : undefined}
        onMessageChange={action.mode === "message" ? setMessageText : undefined}
        selectionOptions={action.mode === "selection" ? action.selection?.options : undefined}
        selectionValue={action.mode === "selection" ? selectionValue : undefined}
        onSelectionChange={action.mode === "selection" ? setSelectionValue : undefined}
        selectionNote={action.mode === "selection" ? action.selection?.note : undefined}
        selectionHeader={
          action.mode === "selection" ? action.selection?.header : action.mode === "round3_setup" ? action.round3?.header : undefined
        }
        selectionLabel={action.mode === "selection" ? action.selection?.label : undefined}
        allowSkip={action.mode === "selection" ? action.selection?.allowSkip : undefined}
        skipChecked={action.mode === "selection" ? skipSecondConvo : undefined}
        onSkipChange={action.mode === "selection" ? setSkipSecondConvo : undefined}
        skipLabel={action.mode === "selection" ? action.selection?.skipLabel : undefined}
        secondaryLabel={action.mode === "message" ? action.message?.secondaryLabel : undefined}
        onSecondaryAction={action.mode === "message" ? handleSecondaryAction : undefined}
        secondaryDisabled={action.mode === "message" ? false : undefined}
        helperText={action.mode === "message" ? action.message?.helperText : undefined}
        primaryLabelOverride={action.mode === "round3_setup" ? action.round3?.buttonLabel : undefined}
        extraContent={
          action.mode === "round3_setup" ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <label>
                Next issue
                <select
                  value={selectedIssueId}
                  onChange={(e) => setSelectedIssueId(e.target.value)}
                  style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
                >
                  <option value="">-- choose --</option>
                  {(action.round3?.issues || []).map((issueId) => (
                    <option key={issueId} value={issueId}>
                      {issueId}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Human placement
                <select
                  value={humanPlacement}
                  onChange={(e) => setHumanPlacement(e.target.value as "first" | "random" | "skip")}
                  style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
                >
                  <option value="first">first</option>
                  <option value="random">random</option>
                  <option value="skip">skip</option>
                </select>
              </label>
            </div>
          ) : undefined
        }
      />
    </div>
  );
};

function deriveRoundLabel(status: string | null): string {
  if (!status) return "(unknown)";
  if (status.startsWith("ROUND_1")) return "1";
  if (status.startsWith("ROUND_2")) return "2";
  if (status.startsWith("ROUND_3") || status.startsWith("ISSUE_")) return "3";
  return "(unknown)";
}

function deriveIssueTitle(state: any, roundLabel: string): string | null {
  if (roundLabel !== "3") return null;
  const title = state?.round3?.active_issue?.issue_title;
  return typeof title === "string" && title.trim() ? title : null;
}

function deriveNextIndicator(state: any, confirmedRoleId: string): { label: string; hint?: string | null } {
  const status: string | null = state?.status ?? null;
  const humanRoleId = state?.human_role_id || confirmedRoleId;
  if (!status) {
    return { label: "(unknown)" };
  }

  if (status === "ROUND_1_OPENING_STATEMENTS") {
    const order = Array.isArray(state?.round1?.speaker_order) ? state.round1.speaker_order : [];
    const cursor = typeof state?.round1?.cursor === "number" ? state.round1.cursor : null;
    if (cursor !== null && cursor >= 0 && cursor < order.length) {
      const roleId = order[cursor];
      return { label: roleId === humanRoleId ? "You" : roleId, hint: "opening statement" };
    }
    return { label: "(unknown)" };
  }

  if (status === "ISSUE_DEBATE_ROUND_1" || status === "ISSUE_DEBATE_ROUND_2") {
    const queue = Array.isArray(state?.round3?.active_issue?.debate_queue)
      ? state.round3.active_issue.debate_queue
      : [];
    const cursor = typeof state?.round3?.active_issue?.debate_cursor === "number"
      ? state.round3.active_issue.debate_cursor
      : null;
    if (cursor !== null && cursor >= 0 && cursor < queue.length) {
      const roleId = queue[cursor];
      return { label: roleId === humanRoleId ? "You" : roleId, hint: "debate speech" };
    }
    return { label: "(unknown)" };
  }

  if (status === "ISSUE_VOTE") {
    const order = Array.isArray(state?.round3?.active_issue?.vote_order) ? state.round3.active_issue.vote_order : [];
    const idx = typeof state?.round3?.active_issue?.next_voter_index === "number"
      ? state.round3.active_issue.next_voter_index
      : null;
    if (idx !== null && idx >= 0 && idx < order.length) {
      const roleId = order[idx];
      return { label: roleId === humanRoleId ? "You" : roleId, hint: "vote" };
    }
    return { label: "(unknown)" };
  }

  if (status === "ROUND_2_SELECT_CONVO_1") {
    return { label: "You", hint: "select conversation partner" };
  }
  if (status === "ROUND_2_SELECT_CONVO_2") {
    return { label: "You", hint: "select conversation partner" };
  }

  return { label: "(unknown)" };
}

function deriveCurrentTurnRole(state: any): string | null {
  const status: string | null = state?.status ?? null;
  if (!status) return null;
  if (status === "ROUND_1_OPENING_STATEMENTS" || status === "ROUND_1_STEP") {
    const round1 = state?.round1;
    const order = Array.isArray(round1?.speaker_order) ? round1.speaker_order : [];
    const cursor = typeof round1?.cursor === "number" ? round1.cursor : null;
    if (cursor !== null && cursor >= 0 && cursor < order.length) {
      return order[cursor] || null;
    }
  }
  if (status === "ISSUE_DEBATE_ROUND_1" || status === "ISSUE_DEBATE_ROUND_2") {
    const activeIssue = state?.round3?.active_issue;
    const queue = Array.isArray(activeIssue?.debate_queue) ? activeIssue.debate_queue : [];
    const cursor = typeof activeIssue?.debate_cursor === "number" ? activeIssue.debate_cursor : null;
    if (cursor !== null && cursor >= 0 && cursor < queue.length) {
      return queue[cursor] || null;
    }
  }
  if (status === "ISSUE_VOTE") {
    const activeIssue = state?.round3?.active_issue;
    const voteOrder = Array.isArray(activeIssue?.vote_order) ? activeIssue.vote_order : [];
    const idx = typeof activeIssue?.next_voter_index === "number" ? activeIssue.next_voter_index : null;
    if (idx !== null && idx >= 0 && idx < voteOrder.length) {
      return voteOrder[idx] || null;
    }
  }
  return null;
}

type ActionConfig = {
  label: string;
  enabled: boolean;
  event: AdvanceEvent | null;
  payload: Record<string, unknown>;
  disabledReason: string | null;
  mode: "advance" | "message" | "selection" | "round3_setup";
  placeholder?: string;
  message?: {
    payloadKey: "text" | "content";
    secondaryEvent?: AdvanceEvent;
    secondaryLabel?: string;
    helperText?: string;
  };
  selection?: {
    options: { value: string; label: string }[];
    note?: string;
    allowSkip: boolean;
    skipLabel?: string;
    selectEvent: AdvanceEvent;
    skipEvent?: AdvanceEvent;
    payloadKey?: string;
    header?: string;
    label?: string;
  };
  round3?: {
    event: AdvanceEvent;
    issues: string[];
    defaultIssueId?: string;
    header: string;
    buttonLabel: string;
  };
};

function deriveActionConfig(state: any, confirmedRoleId: string): ActionConfig {
  const status: string | null = state?.status ?? null;
  const humanRoleId = state?.human_role_id || confirmedRoleId;
  const closedIssues: string[] = Array.isArray(state?.round3?.closed_issues) ? state.round3.closed_issues : [];
  if (!status) {
    return {
      label: "Continue",
      enabled: false,
      event: null,
      payload: {},
      disabledReason: "Status unknown.",
      mode: "advance",
    };
  }

  if (status === "ROLE_SELECTION") {
    if (!confirmedRoleId) {
      return disabledAction(status, "No confirmed role available.");
    }
    return {
      label: "Confirm role",
      enabled: true,
      event: "ROLE_CONFIRMED",
      payload: { human_role_id: confirmedRoleId },
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ROUND_1_SETUP") {
    return {
      label: "Start Round 1",
      enabled: true,
      event: "ROUND_1_READY",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ROUND_1_OPENING_STATEMENTS") {
    const round1 = state?.round1;
    const order = Array.isArray(round1?.speaker_order) ? round1.speaker_order : [];
    const cursor = typeof round1?.cursor === "number" ? round1.cursor : null;
    if (cursor === null || order.length === 0) {
      return disabledAction(status, "Opening order unavailable.");
    }
    if (cursor >= order.length) {
      return {
        label: "Continue",
        enabled: true,
        event: "ROUND_1_STEP",
        payload: {},
        disabledReason: null,
        mode: "advance",
      };
    }
    const speaker = order[cursor];
    if (!humanRoleId) {
      return disabledAction(status, "Human role not set.");
    }
    if (speaker === humanRoleId) {
      return {
        label: "Submit opening statement",
        enabled: true,
        event: "HUMAN_OPENING_STATEMENT",
        payload: {},
        disabledReason: "Message required.",
        mode: "message",
        placeholder: "Enter your opening statement...",
        message: { payloadKey: "text" },
      };
    }
    return {
      label: "Advance opening statement",
      enabled: true,
      event: "ROUND_1_STEP",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ROUND_2_SETUP") {
    return {
      label: "Start Round 2",
      enabled: true,
      event: "ROUND_2_READY",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ROUND_2_SELECT_CONVO_1") {
    const options = deriveRound2PartnerOptions(state, humanRoleId, null);
    if (options.length === 0) {
      return disabledAction(status, "No partner options available.");
    }
    return {
      label: "Select partner",
      enabled: true,
      event: "CONVO_1_SELECTED",
      payload: {},
      disabledReason: null,
      mode: "selection",
      selection: {
        options,
        note: "Partner options are derived from roles (temporary).",
        allowSkip: false,
        selectEvent: "CONVO_1_SELECTED",
      },
    };
  }

  if (status === "ROUND_2_SELECT_CONVO_2") {
    const convo1Partner = state?.round2?.convo1?.partner_role;
    const options = deriveRound2PartnerOptions(state, humanRoleId, convo1Partner);
    if (options.length === 0) {
      return disabledAction(status, "No partner options available.");
    }
    return {
      label: "Select partner",
      enabled: true,
      event: "CONVO_2_SELECTED",
      payload: {},
      disabledReason: null,
      mode: "selection",
      selection: {
        options,
        note: "Partner options are derived from roles (temporary).",
        allowSkip: true,
        skipLabel: "Skip second conversation",
        selectEvent: "CONVO_2_SELECTED",
        skipEvent: "CONVO_2_SKIPPED",
      },
    };
  }

  if (status === "ROUND_2_CONVERSATION_ACTIVE") {
    const activeIdx = state?.round2?.active_convo_index;
    const messageEvent: AdvanceEvent = activeIdx === 2 ? "CONVO_2_MESSAGE" : "CONVO_1_MESSAGE";
    return {
      label: "Send message",
      enabled: true,
      event: messageEvent,
      payload: {},
      disabledReason: null,
      mode: "message",
      placeholder: "Enter your message...",
      message: {
        payloadKey: "content",
        secondaryEvent: "CONVO_END_EARLY",
        secondaryLabel: "End conversation early",
        helperText: "Backend drives turns; send when status allows.",
      },
    };
  }

  if (status === "ROUND_2_WRAP_UP") {
    return {
      label: "Proceed to Round 3",
      enabled: true,
      event: "ROUND_2_WRAP_READY",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ROUND_3_SETUP") {
    const issues = Array.isArray(state?.round3?.issues) ? state.round3.issues : [];
    const activeIssueId = state?.round3?.active_issue?.issue_id;
    const nextIssue =
      issues.find((issueId: string) => issueId !== activeIssueId && !closedIssues.includes(issueId)) ||
      issues[0] ||
      "";
    return {
      label: "Start Issue",
      enabled: issues.length > 0,
      event: null,
      payload: {},
      disabledReason: issues.length > 0 ? null : "No issues available.",
      mode: "round3_setup",
      round3: {
        event: "ROUND_3_START_ISSUE",
        issues,
        defaultIssueId: nextIssue,
        header: "Round 3 setup",
        buttonLabel: "Start Issue",
      },
    };
  }

  if (status === "ISSUE_INTRO") {
    return {
      label: "Start debate",
      enabled: true,
      event: "ISSUE_INTRO_CONTINUE",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ISSUE_DEBATE_ROUND_1" || status === "ISSUE_DEBATE_ROUND_2" || status === "ISSUE_VOTE") {
    const activeIssue = state?.round3?.active_issue;
    const queue = Array.isArray(activeIssue?.debate_queue) ? activeIssue.debate_queue : [];
    const cursor = typeof activeIssue?.debate_cursor === "number" ? activeIssue.debate_cursor : null;
    if (cursor === null || queue.length === 0) {
      if (status !== "ISSUE_VOTE") {
        return disabledAction(status, "Debate order unavailable.");
      }
    }
    if (status === "ISSUE_VOTE") {
      const voteOrder = Array.isArray(activeIssue?.vote_order) ? activeIssue.vote_order : [];
      const nextIdx = typeof activeIssue?.next_voter_index === "number" ? activeIssue.next_voter_index : null;
      const votes = activeIssue?.votes;
      const isHumanVoteTurn =
        !!humanRoleId &&
        nextIdx !== null &&
        Array.isArray(voteOrder) &&
        voteOrder[nextIdx] === humanRoleId &&
        votes !== undefined;
      if (isHumanVoteTurn) {
        const options = Array.isArray(activeIssue?.options) ? activeIssue.options : [];
        const proposedId = activeIssue?.proposed_option_id;
        const proposedLabel =
          options.find((o: any) => o.option_id === proposedId)?.label ||
          options.find((o: any) => o.option_id === proposedId)?.short_description ||
          proposedId;
        const header = proposedId ? `Vote on proposal ${proposedId}: ${proposedLabel || ""}` : "Vote on proposal";
        return {
          label: "Submit Vote",
          enabled: true,
          event: "HUMAN_VOTE",
          payload: {},
          disabledReason: null,
          mode: "selection",
          selection: {
            options: [
              { value: "YES", label: "YES" },
              { value: "NO", label: "NO" },
            ],
            allowSkip: false,
            selectEvent: "HUMAN_VOTE",
            payloadKey: "vote",
            header,
            label: "Vote",
          },
        };
      }
      return {
        label: "Debate step",
        enabled: true,
        event: "ISSUE_DEBATE_STEP",
        payload: {},
        disabledReason: null,
        mode: "advance",
      };
    }

    if (cursor >= queue.length) {
      return {
        label: "Continue",
        enabled: true,
        event: "ISSUE_DEBATE_STEP",
        payload: {},
        disabledReason: null,
        mode: "advance",
      };
    }
    const speaker = queue[cursor];
    if (!humanRoleId) {
      return disabledAction(status, "Human role not set.");
    }
    if (speaker === humanRoleId) {
      return {
        label: "Submit debate message",
        enabled: true,
        event: "HUMAN_DEBATE_MESSAGE",
        payload: {},
        disabledReason: "Message required.",
        mode: "message",
        placeholder: "Enter your debate message...",
        message: { payloadKey: "text" },
      };
    }
    return {
      label: "Debate step",
      enabled: true,
      event: "ISSUE_DEBATE_STEP",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ISSUE_RESOLUTION") {
    return {
      label: "Continue",
      enabled: true,
      event: "ISSUE_RESOLUTION_CONTINUE",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  if (status === "ISSUE_POSITION_FINALIZATION" || status === "ISSUE_PROPOSAL_SELECTION") {
    return {
      label: "Continue",
      enabled: true,
      event: "CONTINUE",
      payload: {},
      disabledReason: null,
      mode: "advance",
    };
  }

  return disabledAction(status, `Status ${status} not actionable.`);
}

function disabledAction(status: string, reason: string): ActionConfig {
  return {
    label: "Continue",
    enabled: false,
    event: null,
    payload: {},
    disabledReason: reason || `Status ${status} not actionable.`,
    mode: "advance",
  };
}

function deriveRound2PartnerOptions(
  state: any,
  humanRoleId: string | null,
  excludeRoleId: string | null
): { value: string; label: string }[] {
  // TODO: Replace with backend-provided round2.available_partners + chooser_role_id once available.
  const roles = state?.roles;
  if (!roles || typeof roles !== "object") return [];
  const countryRoles: string[] = [];
  const ngoRoles: string[] = [];
  const chairRoles: string[] = [];
  Object.keys(roles).forEach((roleId) => {
    const type = roles[roleId]?.type;
    if (type === "country") {
      countryRoles.push(roleId);
    } else if (type === "ngo") {
      ngoRoles.push(roleId);
    } else if (type === "chair") {
      chairRoles.push(roleId);
    }
  });
  countryRoles.sort();
  ngoRoles.sort();
  const excluded = new Set<string>();
  if (humanRoleId) excluded.add(humanRoleId);
  if (excludeRoleId) excluded.add(excludeRoleId);
  chairRoles.forEach((roleId) => excluded.add(roleId));
  const ordered = [...countryRoles, ...ngoRoles].filter((roleId) => !excluded.has(roleId));
  return ordered.map((roleId) => ({ value: roleId, label: roleId }));
}
