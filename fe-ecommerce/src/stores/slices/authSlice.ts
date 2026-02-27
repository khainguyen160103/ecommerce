import { createSlice, type PayloadAction, createAsyncThunk } from '@reduxjs/toolkit'
import { User } from '@/types/user'
type AuthState = {
  user: User | null
}
const initialState: AuthState = {
  user: null
};


const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredential: (state, action: PayloadAction<{ user: User }>) => {
      console.log("user in store: ", action.payload.user)
      state.user = action.payload.user
    }
  },
});

export const { setCredential } = authSlice.actions
export default authSlice.reducer