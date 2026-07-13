import { configureStore } from "@reduxjs/toolkit";

import interactionsReducer from "./interactionsSlice";
import chatReducer from "./chatSlice";
import uiReducer from "./uiSlice";

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    ui: uiReducer,
  },
});
