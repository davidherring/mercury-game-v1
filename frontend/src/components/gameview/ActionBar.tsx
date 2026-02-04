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
    <footer className="action-bar">
      {mode === "message" ? (
        <div className="action-stack">
          <textarea
            value={messageValue}
            onChange={(e) => onMessageChange?.(e.target.value)}
            rows={3}
            placeholder={messagePlaceholder}
            className="textarea"
          />
          <div className="action-row">
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              className="btn btn-primary"
              data-loading={loading}
            >
              {loading ? "Submitting..." : label}
            </button>
            {secondaryLabel && onSecondaryAction && (
              <button
                type="button"
                onClick={onSecondaryAction}
                disabled={secondaryDisabled || loading}
                className="btn btn-secondary"
                data-loading={loading}
              >
                {secondaryLabel}
              </button>
            )}
            {!enabled && disabledReason && (
              <div className="text-small text-muted">{disabledReason}</div>
            )}
          </div>
        </div>
      ) : mode === "selection" ? (
        <div className="action-stack">
          {selectionHeader && <div className="text-small text-muted">{selectionHeader}</div>}
          <label className="field">
            {selectionLabel || "Partner"}
            <select
              value={selectionValue || ""}
              onChange={(e) => onSelectionChange?.(e.target.value)}
              disabled={allowSkip && skipChecked}
              className="select"
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
            <label className="text-small text-muted">
              <input
                type="checkbox"
                checked={skipChecked}
                onChange={(e) => onSkipChange?.(e.target.checked)}
                className="checkbox"
              />
              {skipLabel || "Skip second conversation"}
            </label>
          )}
          {extraContent}
          {selectionNote && <div className="text-small text-muted">{selectionNote}</div>}
          <div className="action-row">
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              className="btn btn-primary"
              data-loading={loading}
            >
              {loading ? "Submitting..." : primaryLabelOverride || label}
            </button>
            {secondaryLabel && onSecondaryAction && (
              <button
                type="button"
                onClick={onSecondaryAction}
                disabled={secondaryDisabled || loading}
                className="btn btn-secondary"
                data-loading={loading}
              >
                {secondaryLabel}
              </button>
            )}
            {!enabled && disabledReason && (
              <div className="text-small text-muted">{disabledReason}</div>
            )}
          </div>
        </div>
      ) : mode === "round3_setup" ? (
        <div className="action-stack">
          {selectionHeader && <div className="text-small text-muted">{selectionHeader}</div>}
          {extraContent}
          <div className="action-row">
            <button
              type="button"
              onClick={onAction}
              disabled={!enabled || loading}
              className="btn btn-primary"
              data-loading={loading}
            >
              {loading ? "Submitting..." : primaryLabelOverride || label}
            </button>
            {!enabled && disabledReason && (
              <div className="text-small text-muted">{disabledReason}</div>
            )}
          </div>
        </div>
      ) : (
        <div className="action-row">
          <button
            type="button"
            onClick={onAction}
            disabled={!enabled || loading}
            className="btn btn-primary"
            data-loading={loading}
          >
            {loading ? "Advancing..." : label}
          </button>
          {secondaryLabel && onSecondaryAction && (
            <button
              type="button"
              onClick={onSecondaryAction}
              disabled={secondaryDisabled || loading}
              className="btn btn-secondary"
              data-loading={loading}
            >
              {secondaryLabel}
            </button>
          )}
          {!enabled && disabledReason && (
            <div className="text-small text-muted">{disabledReason}</div>
          )}
        </div>
      )}
      {helperText && <div className="text-small text-muted stack-sm">{helperText}</div>}
      {errorMessage && (
        <div className="text-small text-error stack-sm">{errorMessage}</div>
      )}
    </footer>
  );
};
