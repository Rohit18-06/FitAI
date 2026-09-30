import api from './client';
import type { RegisterRequest, LoginRequest, LoginResponse, UserResponse } from '../types';

export const authApi = {
  register: (data: RegisterRequest) =>
    api.post<LoginResponse>('/auth/register', data).then(r => r.data),

  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data).then(r => r.data),

  getMe: () =>
    api.get<UserResponse>('/auth/me').then(r => r.data),
};
