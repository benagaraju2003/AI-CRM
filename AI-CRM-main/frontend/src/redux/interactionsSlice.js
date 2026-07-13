import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

import api from "../services/api";

export const fetchInteractions = createAsyncThunk(
  "interactions/fetchAll",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await api.get("/interactions");
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Failed to load interactions.");
    }
  }
);

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await api.post("/interaction", payload);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Failed to log interaction.");
    }
  }
);

export const updateInteraction = createAsyncThunk(
  "interactions/update",
  async ({ id, payload }, { rejectWithValue }) => {
    try {
      const { data } = await api.put(`/interaction/${id}`, payload);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Failed to update interaction.");
    }
  }
);

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    items: [],
    status: "idle", // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.error = action.payload;
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const idx = state.items.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export default interactionsSlice.reducer;
