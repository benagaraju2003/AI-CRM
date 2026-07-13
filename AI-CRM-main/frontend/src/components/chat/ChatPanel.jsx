import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { sendChatMessage } from "../../redux/chatSlice";
import { fetchInteractions } from "../../redux/interactionsSlice";

const TOOL_LABELS = {
  log_interaction: "Interaction logged",
  edit_interaction: "Interaction updated",
  get_hcp_profile: "Profile retrieved",
  schedule_followup: "Follow-up scheduled",
  interaction_summary: "Summary generated",
};

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((state) => state.chat);
  const [draft, setDraft] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const text = draft.trim();
    if (!text || status === "loading") return;
    setDraft("");
    const result = await dispatch(sendChatMessage(text));
    // If the agent's tool wrote/edited data, refresh the shared interactions list
    if (result?.payload?.tool_used && result.payload.data?.success) {
      dispatch(fetchInteractions());
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.headerRow}>
        <span style={styles.aiDot} />
        <div>
          <div style={styles.title}>AI Assistant</div>
          <div style={styles.subtitle}>Log interactions via chat</div>
        </div>
      </div>

      <div ref={scrollRef} style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.placeholder}>
            Try: <em>"Met Dr Sharma today, discussed CardioX, positive sentiment, follow up next Friday."</em>
          </div>
        )}
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              ...styles.bubble,
              ...(m.role === "user" ? styles.bubbleUser : styles.bubbleAssistant),
              ...(m.isError ? styles.bubbleError : {}),
            }}
          >
            {m.content}
            {m.toolUsed && (
              <div style={styles.toolTag}>
                {TOOL_LABELS[m.toolUsed] || m.toolUsed}
              </div>
            )}
          </div>
        ))}
        {status === "loading" && <div style={styles.loadingBubble}>Thinking…</div>}
      </div>

      <div style={styles.inputRow}>
        <input
          style={styles.input}
          placeholder="Describe interaction..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button style={styles.sendBtn} onClick={handleSend} disabled={status === "loading"}>
          Log
        </button>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-lg)",
    display: "flex",
    flexDirection: "column",
    height: "100%",
    boxShadow: "var(--shadow-sm)",
    overflow: "hidden",
  },
  headerRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: 16,
    borderBottom: "1px solid var(--color-border)",
  },
  aiDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "var(--color-primary)",
    flexShrink: 0,
  },
  title: {
    fontSize: 14,
    fontWeight: 700,
    color: "var(--color-text)",
  },
  subtitle: {
    fontSize: 11,
    color: "var(--color-text-muted)",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    gap: 10,
    minHeight: 200,
  },
  placeholder: {
    fontSize: 13,
    color: "var(--color-text-muted)",
    lineHeight: 1.5,
  },
  bubble: {
    padding: "10px 12px",
    borderRadius: "var(--radius-md)",
    fontSize: 13.5,
    lineHeight: 1.5,
    maxWidth: "90%",
  },
  bubbleUser: {
    alignSelf: "flex-end",
    background: "var(--color-primary-tint)",
    color: "var(--color-text)",
  },
  bubbleAssistant: {
    alignSelf: "flex-start",
    background: "var(--color-surface-sunken)",
    color: "var(--color-text)",
  },
  bubbleError: {
    background: "var(--color-negative-tint)",
    color: "var(--color-negative)",
  },
  toolTag: {
    marginTop: 6,
    display: "inline-block",
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: 0.3,
    textTransform: "uppercase",
    color: "var(--color-primary)",
    background: "var(--color-primary-tint)",
    padding: "2px 8px",
    borderRadius: 20,
  },
  loadingBubble: {
    alignSelf: "flex-start",
    fontSize: 13,
    color: "var(--color-text-muted)",
    fontStyle: "italic",
  },
  inputRow: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid var(--color-border)",
  },
  input: {
    flex: 1,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-border)",
    fontSize: 13.5,
  },
  sendBtn: {
    padding: "10px 16px",
    borderRadius: "var(--radius-sm)",
    border: "none",
    background: "var(--color-primary)",
    color: "#fff",
    fontWeight: 600,
    fontSize: 13,
  },
};
