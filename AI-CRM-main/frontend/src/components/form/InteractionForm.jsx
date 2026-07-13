import React, { useState } from "react";
import { useDispatch } from "react-redux";

import { createInteraction } from "../../redux/interactionsSlice";
import { showToast } from "../../redux/uiSlice";

const EMPTY_FORM = {
  hcp_name: "",
  interaction_type: "meeting",
  interaction_date: new Date().toISOString().slice(0, 16),
  attendees: "",
  topics_discussed: "",
  products_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "neutral",
  outcomes: "",
  follow_up_actions: "",
};

export default function InteractionForm() {
  const dispatch = useDispatch();
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.hcp_name.trim()) {
      setFormError("HCP name is required.");
      return;
    }
    setFormError(null);
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        interaction_date: new Date(form.interaction_date).toISOString(),
      };
      await dispatch(createInteraction(payload)).unwrap();
      dispatch(showToast({ type: "success", message: "Interaction logged successfully." }));
      setForm(EMPTY_FORM);
    } catch (err) {
      setFormError(typeof err === "string" ? err : "Failed to log interaction.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.card}>
      <h2 style={styles.cardTitle}>Interaction Details</h2>

      <div style={styles.grid2}>
        <Field label="HCP Name" required>
          <input
            style={styles.input}
            placeholder="Search or enter HCP name..."
            value={form.hcp_name}
            onChange={handleChange("hcp_name")}
          />
        </Field>

        <Field label="Interaction Type">
          <select style={styles.input} value={form.interaction_type} onChange={handleChange("interaction_type")}>
            <option value="meeting">Meeting</option>
            <option value="call">Call</option>
            <option value="email">Email</option>
            <option value="conference">Conference</option>
            <option value="other">Other</option>
          </select>
        </Field>
      </div>

      <Field label="Date &amp; Time">
        <input
          type="datetime-local"
          style={styles.input}
          value={form.interaction_date}
          onChange={handleChange("interaction_date")}
        />
      </Field>

      <Field label="Attendees">
        <input
          style={styles.input}
          placeholder="Enter names..."
          value={form.attendees}
          onChange={handleChange("attendees")}
        />
      </Field>

      <Field label="Topics Discussed">
        <textarea
          style={styles.textarea}
          rows={3}
          placeholder="Enter key discussion points..."
          value={form.topics_discussed}
          onChange={handleChange("topics_discussed")}
        />
      </Field>

      <div style={styles.grid2}>
        <Field label="Products Discussed">
          <input
            style={styles.input}
            placeholder="e.g. CardioX, NeuroPlus"
            value={form.products_discussed}
            onChange={handleChange("products_discussed")}
          />
        </Field>

        <Field label="Materials / Samples Shared">
          <input
            style={styles.input}
            placeholder="e.g. Phase III PDF, sample pack"
            value={form.materials_shared}
            onChange={handleChange("materials_shared")}
          />
        </Field>
      </div>

      <Field label="Observed HCP Sentiment">
        <div style={styles.sentimentRow}>
          {["positive", "neutral", "negative"].map((s) => (
            <label key={s} style={styles.sentimentOption}>
              <input
                type="radio"
                name="sentiment"
                value={s}
                checked={form.sentiment === s}
                onChange={handleChange("sentiment")}
              />
              <span style={{ textTransform: "capitalize" }}>{s}</span>
            </label>
          ))}
        </div>
      </Field>

      <Field label="Outcomes">
        <textarea
          style={styles.textarea}
          rows={2}
          placeholder="Key outcomes or agreements..."
          value={form.outcomes}
          onChange={handleChange("outcomes")}
        />
      </Field>

      <Field label="Follow-up Actions">
        <textarea
          style={styles.textarea}
          rows={2}
          placeholder="Enter next steps or tasks..."
          value={form.follow_up_actions}
          onChange={handleChange("follow_up_actions")}
        />
      </Field>

      {formError && <div style={styles.errorBox}>{formError}</div>}

      <button type="submit" disabled={submitting} style={styles.submitBtn}>
        {submitting ? "Logging..." : "Log Interaction"}
      </button>
    </form>
  );
}

function Field({ label, required, children }) {
  return (
    <div style={styles.field}>
      <label style={styles.label}>
        {label} {required && <span style={{ color: "var(--color-negative)" }}>*</span>}
      </label>
      {children}
    </div>
  );
}

const styles = {
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-lg)",
    padding: 24,
    boxShadow: "var(--shadow-sm)",
  },
  cardTitle: {
    margin: "0 0 20px",
    fontSize: 16,
    fontWeight: 700,
    color: "var(--color-text)",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
  },
  field: {
    marginBottom: 16,
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
    letterSpacing: 0.3,
  },
  input: {
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-border)",
    fontSize: 14,
    color: "var(--color-text)",
    background: "var(--color-surface)",
  },
  textarea: {
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-border)",
    fontSize: 14,
    color: "var(--color-text)",
    resize: "vertical",
    fontFamily: "inherit",
  },
  sentimentRow: {
    display: "flex",
    gap: 16,
  },
  sentimentOption: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontSize: 14,
    color: "var(--color-text)",
  },
  errorBox: {
    background: "var(--color-negative-tint)",
    color: "var(--color-negative)",
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    fontSize: 13,
    marginBottom: 12,
  },
  submitBtn: {
    width: "100%",
    padding: "12px 16px",
    borderRadius: "var(--radius-sm)",
    border: "none",
    background: "var(--color-primary)",
    color: "#fff",
    fontWeight: 600,
    fontSize: 14,
  },
};
