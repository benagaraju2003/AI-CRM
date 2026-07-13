import React from "react";

import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <div style={styles.shell}>
      <Sidebar />
      <div style={styles.main}>
        <Header />
        <div style={styles.content}>
          <Dashboard />
        </div>
      </div>
    </div>
  );
}

const styles = {
  shell: {
    display: "flex",
    minHeight: "100vh",
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    minWidth: 0,
  },
  content: {
    flex: 1,
    overflowY: "auto",
  },
};
