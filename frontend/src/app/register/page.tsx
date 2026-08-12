'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { User, Mail, Lock, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { register, login } = useAuth();

  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(nome, email, senha);
      // Auto login após cadastro
      await login(email, senha);
      router.push('/agendar');
    } catch (err: any) {
      setError(err.message || 'Erro ao realizar cadastro. Tente com outro e-mail.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 p-8 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-2xl space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 mx-auto rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
          <User className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white">Criar Nova Conta</h1>
        <p className="text-sm text-slate-400">Preencha seus dados para começar a agendar</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Nome Completo
          </label>
          <div className="relative">
            <User className="w-5 h-5 absolute left-3.5 top-3.5 text-slate-500" />
            <input
              type="text"
              required
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              placeholder="Maria Silva"
              className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            E-mail
          </label>
          <div className="relative">
            <Mail className="w-5 h-5 absolute left-3.5 top-3.5 text-slate-500" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seuemail@exemplo.com"
              className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Senha
          </label>
          <div className="relative">
            <Lock className="w-5 h-5 absolute left-3.5 top-3.5 text-slate-500" />
            <input
              type="password"
              required
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors text-sm"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 px-4 bg-gradient-to-r from-brand-600 to-pink-600 hover:from-brand-500 hover:to-pink-500 text-white font-semibold rounded-xl shadow-lg shadow-brand-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? 'Criando Conta...' : 'Cadastrar Conta'}
          {!loading && <ArrowRight className="w-4 h-4" />}
        </button>
      </form>

      <div className="text-center pt-4 border-t border-slate-800/80">
        <p className="text-sm text-slate-400">
          Já possui conta?{' '}
          <Link href="/login" className="font-semibold text-brand-400 hover:underline">
            Faça login
          </Link>
        </p>
      </div>
    </div>
  );
}
