import React from "react";
import { useSelector } from "react-redux";

export default function Header() {
  const activeView = useSelector((state) => state.ui.activeView);

  const titles = {
    log: {
      title: "Log HCP Interaction",
      subtitle: "Use the structured form or describe it to the AI assistant — both save to the same record.",
    },
    history: {
      title: "Interaction History",
      subtitle: "All logged interactions across form and chat entries.",
    },
  };

  const { title, subtitle } = titles[activeView] || titles.log;

  return (
    <header style={styles.header}>
      <div>
        <h1 style={styles.title}>{title}</h1>
        <p style={styles.subtitle}>{subtitle}</p>
      </div>
    </header>
  );
}

const styles = {
  header: {
    padding: "24px 32px",
    borderBottom: "1px solid var(--color-border)",
    background: "var(--color-surface)",
  },
  title: {
    margin: 0,
    fontSize: 22,
    fontWeight: 700,
    color: "var(--color-text)",
  },
  subtitle: {
    margin: "4px 0 0",
    fontSize: 13,
    color: "var(--color-text-muted)",
  },
};
