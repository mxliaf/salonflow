'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiFetch } from './api';

export interface User {
  id: number;
  nome: string;
  email: string;
  role: 'CLIENTE' | 'ADMIN' | 'FUNCIONARIO';
  data_criacao: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, senha: string) => Promise<User>;
  register: (nome: string, email: string, senha: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('salonflow_token');
    const savedUser = localStorage.getItem('salonflow_user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('salonflow_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, senha: string): Promise<User> => {
    const data = await apiFetch<{ access_token: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, senha }),
    });

    localStorage.setItem('salonflow_token', data.access_token);
    localStorage.setItem('salonflow_user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const register = async (nome: string, email: string, senha: string): Promise<void> => {
    await apiFetch('/api/auth/cadastrar', {
      method: 'POST',
      body: JSON.stringify({ nome, email, senha, role: 'CLIENTE' }),
    });
  };

  const logout = () => {
    localStorage.removeItem('salonflow_token');
    localStorage.removeItem('salonflow_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
}
