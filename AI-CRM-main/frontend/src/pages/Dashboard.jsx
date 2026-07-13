import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import InteractionForm from "../components/form/InteractionForm";
import ChatPanel from "../components/chat/ChatPanel";
import InteractionTable from "../components/history/InteractionTable";
import { fetchInteractions } from "../redux/interactionsSlice";
import { clearToast } from "../redux/uiSlice";

export default function Dashboard() {
  const dispatch = useDispatch();
  const activeView = useSelector((state) => state.ui.activeView);
  const toast = useSelector((state) => state.ui.toast);

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => dispatch(clearToast()), 3000);
      return () => clearTimeout(t);
    }
  }, [toast, dispatch]);

  useEffect(() => {
    if (activeView === "history") {
      dispatch(fetchInteractions());
    }
  }, [activeView, dispatch]);

  return (
    <div style={styles.wrapper}>
      {toast && (
        <div
          style={{
            ...styles.toast,
            ...(toast.type === "error" ? styles.toastError : styles.toastSuccess),
          }}
        >
          {toast.message}
        </div>
      )}

      {activeView === "log" ? (
        <div style={styles.splitGrid}>
          <InteractionForm />
          <ChatPanel />
        </div>
      ) : (
        <InteractionTable />
      )}
    </div>
  );
}

const styles = {
  wrapper: {
    padding: 32,
    position: "relative",
  },
  splitGrid: {
    display: "grid",
    gridTemplateColumns: "1.4fr 1fr",
    gap: 24,
    alignItems: "start",
  },
  toast: {
    position: "fixed",
    top: 24,
    right: 32,
    padding: "12px 20px",
    borderRadius: "var(--radius-sm)",
    fontSize: 13.5,
    fontWeight: 600,
    boxShadow: "var(--shadow-md)",
    zIndex: 100,
  },
  toastSuccess: {
    background: "var(--color-positive)",
    color: "#fff",
  },
  toastError: {
    background: "var(--color-negative)",
    color: "#fff",
  },
};
