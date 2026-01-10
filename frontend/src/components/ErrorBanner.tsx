import React from "react";

interface Props {
  message?: string | null;
  onClear?: () => void;
}

export const ErrorBanner: React.FC<Props> = ({ message, onClear }) => {
  if (!message) return null;
  return (
    <div style={{ background: "#fdecea", color: "#611a15", padding: "8px 12px", borderRadius: 4, marginBottom: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span>{message}</span>
      {onClear && (
        <button
          onClick={onClear}
          style={{ marginLeft: 12, padding: "4px 8px", border: "1px solid #611a15", background: "white", color: "#611a15", borderRadius: 4, cursor: "pointer" }}
        >
          Clear
        </button>
      )}
    </div>
  );
};
