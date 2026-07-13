import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

import api from "../services/api";

export const sendChatMessage = createAsyncThunk(
  "chat/sendMessage",
  async (message, { rejectWithValue }) => {
    try {
      const { data } = await api.post("/chat", { message, session_id: "default" });
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "The assistant couldn't respond. Try again.");
    }
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [], // { role: 'user' | 'assistant', content: string, toolUsed?: string }
    status: "idle",
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state, action) => {
        state.status = "loading";
        state.error = null;
        state.messages.push({ role: "user", content: action.meta.arg });
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.messages.push({
          role: "assistant",
          content: action.payload.reply,
          toolUsed: action.payload.tool_used,
          data: action.payload.data,
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
        state.messages.push({
          role: "assistant",
          content: "Something went wrong reaching the assistant. Please try again.",
          isError: true,
        });
      });
  },
});

export default chatSlice.reducer;
