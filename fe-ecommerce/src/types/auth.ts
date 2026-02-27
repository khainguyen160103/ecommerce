
import { baseResponses } from './index';
import {User} from './user'
export type AuthState = {
  accessToken?: string | null;
  refreshToken?: string | null;
  user?: User | null;
};

export interface LoginResponse extends baseResponses<AuthState> {
  message: string;
  payload: AuthState;
}