import React from "react";

export const ActionBar: React.FC<{
  label: string;
  enabled: boolean;
  disabledReason: string | null;
  loading: boolean;
  errorMessage: string | null;
  mode: "advance" | "message" | "selection" | "round3_setup";
  messageValue?: string;
  messagePlaceholder?: string;
  onMessageChange?: (value: string) => void;
  onAction: () => void;
  selectionOptions?: { value: string; label: string }[];
  selectionValue?: string;
  onSelectionChange?: (value: string) => void;
  selectionNote?: string;
  selectionLabel?: string;
  allowSkip?: boolean;
  skipChecked?: boolean;
  onSkipChange?: (checked: boolean) => void;
  skipLabel?: string;
  secondaryLabel?: string;
  onSecondaryAction?: () => void;
  secondaryDisabled?: boolean;
  helperText?: string;
  primaryLabelOverride?: string;
  selectionHeader?: string;
  extraContent?: React.ReactNode;
}> = ({
  label,
  enabled,
  disabledReason,
  loading,
  errorMessage,
  mode,
  messageValue,
  messagePlaceholder,
  onMessageChange,
  onAction,
  selectionOptions,
  selectionValue,
  onSelectionChange,
  selectionNote,
  selectionLabel,
  allowSkip = false,
  skipChecked = false,
  onSkipChange,
  skipLabel,
  secondaryLabel,
  onSecondaryAction,
  secondaryDisabled = false,
  helperText,
  primaryLabelOverride,
  selectionHeader,
  extraContent,
}) => {
  return (
    <footer style={{ borderTop: "1px solid #ddd", padding: "12px 16px", flex: "0 0 auto" }}>
      {mode === "message" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <textarea
            value={messageValue}
            onChange={(e) => onMessageChange?.(e.target.value)}
            rows={3}
            placeholder={messagePlaceholder}
            style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
          />
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              style={{ padding: "8px 12px" }}
            >
              {loading ? "Submitting..." : label}
            </button>
            {secondaryLabel && onSecondaryAction && (
              <button
                type="button"
                onClick={onSecondaryAction}
                disabled={secondaryDisabled || loading}
                style={{ padding: "8px 12px" }}
              >
                {secondaryLabel}
              </button>
            )}
            {!enabled && disabledReason && (
              <div style={{ fontSize: 12, color: "#555" }}>{disabledReason}</div>
            )}
          </div>
        </div>
      ) : mode === "selection" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {selectionHeader && <div style={{ fontSize: 12, color: "#555" }}>{selectionHeader}</div>}
          <label>
            {selectionLabel || "Partner"}
            <select
              value={selectionValue || ""}
              onChange={(e) => onSelectionChange?.(e.target.value)}
              disabled={allowSkip && skipChecked}
              style={{ width: "100%", padding: 8, border: "1px solid #ccc", borderRadius: 4, marginTop: 4 }}
            >
              <option value="">-- choose --</option>
              {(selectionOptions || []).map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          {allowSkip && (
            <label style={{ fontSize: 12, color: "#555" }}>
              <input
                type="checkbox"
                checked={skipChecked}
                onChange={(e) => onSkipChange?.(e.target.checked)}
                style={{ marginRight: 6 }}
              />
              {skipLabel || "Skip second conversation"}
            </label>
          )}
          {extraContent}
          {selectionNote && <div style={{ fontSize: 12, color: "#666" }}>{selectionNote}</div>}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              style={{ padding: "8px 12px" }}
            >
              {loading ? "Submitting..." : primaryLabelOverride || label}
            </button>
            {secondaryLabel && onSecondaryAction && (
              <button
                type="button"
                onClick={onSecondaryAction}
                disabled={secondaryDisabled || loading}
                style={{ padding: "8px 12px" }}
              >
                {secondaryLabel}
              </button>
            )}
            {!enabled && disabledReason && (
              <div style={{ fontSize: 12, color: "#555" }}>{disabledReason}</div>
            )}
          </div>
        </div>
      ) : mode === "round3_setup" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {selectionHeader && <div style={{ fontSize: 12, color: "#555" }}>{selectionHeader}</div>}
          {extraContent}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              style={{ padding: "8px 12px" }}
            >
              {loading ? "Submitting..." : primaryLabelOverride || label}
            </button>
            {!enabled && disabledReason && (
              <div style={{ fontSize: 12, color: "#555" }}>{disabledReason}</div>
            )}
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            type="button"
            onClick={onAction}
            disabled={!enabled || loading}
            style={{ padding: "8px 12px" }}
          >
            {loading ? "Advancing..." : label}
          </button>
          {secondaryLabel && onSecondaryAction && (
            <button
              type="button"
              onClick={onSecondaryAction}
              disabled={secondaryDisabled || loading}
              style={{ padding: "8px 12px" }}
            >
              {secondaryLabel}
            </button>
          )}
          {!enabled && disabledReason && (
            <div style={{ fontSize: 12, color: "#555" }}>{disabledReason}</div>
          )}
        </div>
      )}
      {helperText && <div style={{ marginTop: 6, fontSize: 12, color: "#555" }}>{helperText}</div>}
      {errorMessage && (
        <div style={{ marginTop: 6, fontSize: 12, color: "#b00" }}>{errorMessage}</div>
      )}
    </footer>
  );
};
