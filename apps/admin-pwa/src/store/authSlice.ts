import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { confirmOtp, requestOtp } from "../lib/api";

interface AuthState {
  email: string;
  accessToken: string | null;
  loading: boolean;
  otpRequested: boolean;
  error: string | null;
}

const initialState: AuthState = {
  email: "",
  accessToken: null,
  loading: false,
  otpRequested: false,
  error: null
};

export const requestLoginCode = createAsyncThunk("auth/requestOtp", async (email: string) => {
  await requestOtp(email);
  return email;
});

export const confirmLoginCode = createAsyncThunk(
  "auth/confirmOtp",
  async ({ email, code }: { email: string; code: string }) => {
    const { access } = await confirmOtp(email, code);
    return { email, access };
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.accessToken = null;
      state.otpRequested = false;
      state.email = "";
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(requestLoginCode.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(requestLoginCode.fulfilled, (state, action) => {
        state.loading = false;
        state.email = action.payload;
        state.otpRequested = true;
      })
      .addCase(requestLoginCode.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Не удалось отправить код";
      })
      .addCase(confirmLoginCode.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmLoginCode.fulfilled, (state, action) => {
        state.loading = false;
        state.accessToken = action.payload.access;
        state.email = action.payload.email;
      })
      .addCase(confirmLoginCode.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Не удалось подтвердить код";
      });
  }
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;

