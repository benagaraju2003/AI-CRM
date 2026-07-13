import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    activeView: "log", // 'log' | 'history'
    toast: null, // { type: 'success' | 'error', message: string }
  },
  reducers: {
    setActiveView(state, action) {
      state.activeView = action.payload;
    },
    showToast(state, action) {
      state.toast = action.payload;
    },
    clearToast(state) {
      state.toast = null;
    },
  },
});

export const { setActiveView, showToast, clearToast } = uiSlice.actions;
export default uiSlice.reducer;
