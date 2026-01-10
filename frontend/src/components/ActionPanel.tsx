import React, { useMemo, useState } from "react";
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
  onAdvanced: () => Promise<void> | void;
}

const FALLBACK_ROLES = ["BRA", "CAN", "CHN", "EU", "TZA", "USA"];

export const ActionPanel: React.FC<Props> = ({
  gameId,
  status,
  gameState,
  api,
  onRequest,
  onError,
  onAdvanced,
}) => {
  const [devMode, setDevMode] = useState(false);
  const [rawEvent, setRawEvent] = useState("ROUND_1_READY");
  const [payloadText, setPayloadText] = useState("{}");
  const [selectedRole, setSelectedRole] = useState<string>("");

  const roleOptions = useMemo(() => {
    const rolesObj =
      (gameState && typeof gameState === "object" && (gameState as any).roles) ||
      (gameState && typeof gameState === "object" && (gameState as any).available_roles);
    if (rolesObj && typeof rolesObj === "object") {
      return Object.keys(rolesObj);
    }
    return FALLBACK_ROLES;
  }, [gameState]);

  const doAdvance = async (event: string, payload: Record<string, unknown>) => {
    if (!gameId) {
      onError("No game loaded");
      return;
    }
    const { lastRequest, errorMessage } = await runRequest({
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
    await Promise.resolve(onAdvanced());
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
                {roleOptions.map((r) => (
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
        return (
          <button onClick={() => doAdvance("ROUND_1_STEP", {})} style={{ padding: "8px 12px" }}>
            Next
          </button>
        );
      default:
        return <div style={{ color: "#999" }}>No controls implemented for this status yet.</div>;
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
