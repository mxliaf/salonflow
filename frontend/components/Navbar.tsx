'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Scissors, Calendar, User, LogOut, LayoutDashboard, Sparkles } from 'lucide-react';

export function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isLinkActive = (path: string) => pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-pink-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/25 group-hover:scale-105 transition-transform">
            <Scissors className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-pink-300">
            SalonFlow
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          <Link
            href="/"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isLinkActive('/')
                ? 'bg-slate-800 text-white font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            Serviços
          </Link>
          <Link
            href="/agendar"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              isLinkActive('/agendar')
                ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <Sparkles className="w-4 h-4 text-brand-400" />
            Agendar Horário
          </Link>
          {user && (
            <Link
              href="/meus-agendamentos"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isLinkActive('/meus-agendamentos')
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              Meus Agendamentos
            </Link>
          )}
          {user && (user.role === 'ADMIN' || user.role === 'FUNCIONARIO') && (
            <Link
              href="/admin"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                isLinkActive('/admin')
                  ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 text-purple-400" />
              Painel Admin
            </Link>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-sm font-medium text-slate-200">{user.nome}</span>
                <span className="text-xs text-slate-400 capitalize">{user.role.toLowerCase()}</span>
              </div>
              <button
                onClick={logout}
                title="Sair"
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Entrar
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-brand-600 to-pink-600 hover:from-brand-500 hover:to-pink-500 rounded-lg shadow-md shadow-brand-600/20 transition-all hover:scale-[1.02]"
              >
                Cadastrar
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
