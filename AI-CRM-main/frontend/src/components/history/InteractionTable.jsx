import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { fetchInteractions } from "../../redux/interactionsSlice";

const SENTIMENT_STYLE = {
  positive: { bg: "var(--color-positive-tint)", color: "var(--color-positive)" },
  neutral: { bg: "var(--color-neutral-tint)", color: "var(--color-neutral)" },
  negative: { bg: "var(--color-negative-tint)", color: "var(--color-negative)" },
};

export default function InteractionTable() {
  const dispatch = useDispatch();
  const { items, status, error } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  if (status === "loading" && items.length === 0) {
    return <div style={styles.stateBox}>Loading interactions…</div>;
  }

  if (status === "failed" && items.length === 0) {
    return <div style={{ ...styles.stateBox, color: "var(--color-negative)" }}>{error}</div>;
  }

  if (items.length === 0) {
    return (
      <div style={styles.stateBox}>
        No interactions logged yet. Use the form or AI chat to log your first one.
      </div>
    );
  }

  return (
    <div style={styles.card}>
      <table style={styles.table}>
        <thead>
          <tr>
            {["Date", "HCP", "Type", "Products", "Sentiment", "Source", "Summary"].map((h) => (
              <th key={h} style={styles.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((i) => {
            const sentimentStyle = SENTIMENT_STYLE[i.sentiment] || SENTIMENT_STYLE.neutral;
            return (
              <tr key={i.id} style={styles.tr}>
                <td style={styles.td}>{new Date(i.interaction_date).toLocaleDateString()}</td>
                <td style={styles.td}>HCP #{i.hcp_id}</td>
                <td style={{ ...styles.td, textTransform: "capitalize" }}>{i.interaction_type}</td>
                <td style={styles.td}>{i.products_discussed || "—"}</td>
                <td style={styles.td}>
                  <span
                    style={{
                      ...styles.badge,
                      background: sentimentStyle.bg,
                      color: sentimentStyle.color,
                    }}
                  >
                    {i.sentiment}
                  </span>
                </td>
                <td style={styles.td}>
                  <span
                    style={{
                      ...styles.sourceBadge,
                      ...(i.source === "chat" ? styles.sourceChat : styles.sourceForm),
                    }}
                  >
                    {i.source === "chat" ? "AI Chat" : "Form"}
                  </span>
                </td>
                <td style={{ ...styles.td, maxWidth: 260 }}>
                  {i.summary || i.topics_discussed || "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-lg)",
    overflow: "hidden",
    boxShadow: "var(--shadow-sm)",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 13,
  },
  th: {
    textAlign: "left",
    padding: "12px 16px",
    background: "var(--color-surface-sunken)",
    color: "var(--color-text-muted)",
    fontWeight: 600,
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: 0.3,
    borderBottom: "1px solid var(--color-border)",
  },
  tr: {
    borderBottom: "1px solid var(--color-border)",
  },
  td: {
    padding: "12px 16px",
    color: "var(--color-text)",
    verticalAlign: "top",
  },
  badge: {
    padding: "3px 10px",
    borderRadius: 20,
    fontSize: 11,
    fontWeight: 600,
    textTransform: "capitalize",
  },
  sourceBadge: {
    padding: "3px 10px",
    borderRadius: 20,
    fontSize: 11,
    fontWeight: 600,
  },
  sourceForm: {
    background: "var(--color-secondary-tint)",
    color: "var(--color-secondary)",
  },
  sourceChat: {
    background: "var(--color-primary-tint)",
    color: "var(--color-primary)",
  },
  stateBox: {
    padding: 40,
    textAlign: "center",
    color: "var(--color-text-muted)",
    fontSize: 14,
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-lg)",
  },
};
