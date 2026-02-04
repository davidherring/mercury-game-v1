import React, { useEffect, useMemo, useRef, useState } from "react";
import { CHAIR } from "../../config/roles";

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
  confirmedRoleId?: string | null;
}> = ({ entries, loading, errorMessage, currentTurnRole, confirmedRoleId }) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const hasMountedRef = useRef(false);
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [showNewButton, setShowNewButton] = useState(false);
  const lastEntryKey = entries.length > 0 ? entries[entries.length - 1]?.id || String(entries.length) : "empty";

  useEffect(() => {
    const node = scrollRef.current;
    if (!node) return;

    const distance = node.scrollHeight - node.scrollTop - node.clientHeight;
    const nearBottom = distance < 120;
    setIsNearBottom(nearBottom);
    if (nearBottom) {
      setShowNewButton(false);
    }
  }, [entries.length]);

  useEffect(() => {
    const node = scrollRef.current;
    if (!node) return;

    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      node.scrollTo({ top: node.scrollHeight, behavior: "auto" });
      return;
    }

    if (!isNearBottom) {
      setShowNewButton(true);
      return;
    }

    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [lastEntryKey, isNearBottom]);

  const handleScroll = () => {
    const node = scrollRef.current;
    if (!node) return;
    const distance = node.scrollHeight - node.scrollTop - node.clientHeight;
    const nearBottom = distance < 120;
    setIsNearBottom(nearBottom);
    if (nearBottom) {
      setShowNewButton(false);
    }
  };
  const groupedEntries = useMemo(() => {
    const groups: {
      roleId: string | null;
      phase: string | null;
      items: TranscriptEntry[];
    }[] = [];
    let current: { roleId: string | null; phase: string | null; items: TranscriptEntry[] } | null = null;

    entries.forEach((entry) => {
      const roleId = entry.role_id ?? null;
      const phase = entry.phase ?? null;
      const shouldStart =
        !current || current.roleId !== roleId || current.phase !== phase;

      if (shouldStart) {
        current = { roleId, phase, items: [entry] };
        groups.push(current);
      } else {
        current.items.push(entry);
      }
    });

    return groups;
  }, [entries]);

  const resolveGroupTone = (roleId: string | null): "player" | "system" | "ai" | "unknown" => {
    if (!roleId) return "unknown";
    if (roleId === CHAIR) return "system";
    if (confirmedRoleId && roleId === confirmedRoleId) return "player";
    return "ai";
  };

  return (
    <section className="card transcript-panel">
      <div className="section-header">
        <h2 className="section-title">Transcript</h2>
        {currentTurnRole && <span className="badge">Turn: {currentTurnRole}</span>}
      </div>
      {loading && <div>Loading transcript...</div>}
      {errorMessage && <div className="text-error">Transcript error: {errorMessage}</div>}
      <div className="transcript-list" ref={scrollRef} onScroll={handleScroll}>
        {entries.length === 0 ? (
          <div>{loading ? " " : "No transcript yet."}</div>
        ) : (
          groupedEntries.map((group, idx) => {
            const roleLabel = group.roleId || "?";
            const tone = resolveGroupTone(group.roleId);
            const isCurrent = currentTurnRole && group.roleId === currentTurnRole;
            return (
              <div
                key={`${group.roleId || "unknown"}-${group.phase || "unknown"}-${idx}`}
                className={`transcript-group is-${tone}${isCurrent ? " is-current" : ""}`}
              >
                <div className="transcript-group-header">
                  <span className="role-pill">{roleLabel}</span>
                  {group.phase && <span className="phase-pill">{group.phase}</span>}
                </div>
                <div className="transcript-group-body">
                  {group.items.map((entry, entryIdx) => (
                    <div key={entry.id || entryIdx} className="transcript-message">
                      {entry.content || ""}
                    </div>
                  ))}
                </div>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
      {showNewButton && (
        <button
          type="button"
          className="btn btn-secondary transcript-jump"
          onClick={() => {
            bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
            setShowNewButton(false);
          }}
        >
          New messages ↓
        </button>
      )}
    </section>
  );
};
