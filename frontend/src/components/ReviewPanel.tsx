import React from "react";

interface Props {
  review?: any;
}

export const ReviewPanel: React.FC<Props> = ({ review }) => {
  return (
    <section style={{ padding: "8px 0" }}>
      <h3>Review</h3>
      {!review && <p>Review payload not loaded.</p>}
      {review && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div>
            <strong>Votes:</strong>
            <pre style={{ background: "#f7f7f7", padding: 8, borderRadius: 4, overflow: "auto" }}>
              {JSON.stringify(review.votes, null, 2)}
            </pre>
          </div>
          <div>
            <strong>Transcript:</strong>
            <pre style={{ background: "#f7f7f7", padding: 8, borderRadius: 4, maxHeight: 240, overflow: "auto" }}>
              {JSON.stringify(review.transcript, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </section>
  );
};
