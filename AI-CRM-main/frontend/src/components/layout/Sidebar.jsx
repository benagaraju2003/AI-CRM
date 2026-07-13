import React from "react";
import { useDispatch, useSelector } from "react-redux";

import { setActiveView } from "../../redux/uiSlice";

const NAV_ITEMS = [
  { id: "log", label: "Log Interaction", icon: "📝" },
  { id: "history", label: "Interaction History", icon: "🗂️" },
];

export default function Sidebar() {
  const dispatch = useDispatch();
  const activeView = useSelector((state) => state.ui.activeView);

  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>
        <div style={styles.brandMark}>HCP</div>
        <div>
          <div style={styles.brandName}>Interaction CRM</div>
          <div style={styles.brandSub}>AI-First Field Console</div>
        </div>
      </div>

      <nav style={styles.nav}>
        {NAV_ITEMS.map((item) => {
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => dispatch(setActiveView(item.id))}
              style={{
                ...styles.navItem,
                ...(isActive ? styles.navItemActive : {}),
              }}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      <div style={styles.footer}>
        <div style={styles.footerLabel}>Signed in as</div>
        <div style={styles.footerName}>Field Rep</div>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    width: 240,
    minWidth: 240,
    background: "var(--color-surface)",
    borderRight: "1px solid var(--color-border)",
    display: "flex",
    flexDirection: "column",
    padding: "24px 16px",
    height: "100vh",
    position: "sticky",
    top: 0,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    marginBottom: 32,
    padding: "0 8px",
  },
  brandMark: {
    width: 40,
    height: 40,
    borderRadius: "var(--radius-md)",
    background: "var(--color-primary)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: 13,
    letterSpacing: 0.5,
  },
  brandName: {
    fontWeight: 700,
    fontSize: 15,
    color: "var(--color-text)",
    lineHeight: 1.2,
  },
  brandSub: {
    fontSize: 12,
    color: "var(--color-text-muted)",
  },
  nav: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
  },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    border: "none",
    background: "transparent",
    color: "var(--color-text-muted)",
    fontSize: 14,
    fontWeight: 500,
    textAlign: "left",
  },
  navItemActive: {
    background: "var(--color-primary-tint)",
    color: "var(--color-primary)",
    fontWeight: 600,
  },
  navIcon: {
    fontSize: 16,
  },
  footer: {
    marginTop: "auto",
    padding: "12px 8px",
    borderTop: "1px solid var(--color-border)",
  },
  footerLabel: {
    fontSize: 11,
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  footerName: {
    fontSize: 14,
    fontWeight: 600,
    color: "var(--color-text)",
  },
};
