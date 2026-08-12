'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { apiFetch } from '@/lib/api';
import { Calendar, Clock, Scissors, UserCheck, AlertCircle, XCircle, CheckCircle2, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface Servico {
  nome: string;
  duracao_minutos: number;
  preco: number;
}

interface Funcionario {
  nome: string;
}

interface Agendamento {
  id: number;
  data_hora_inicio: string;
  data_hora_fim: string;
  status: 'PENDENTE' | 'CONFIRMADO' | 'CANCELADO';
  servico?: Servico;
  funcionario?: Funcionario;
}

export default function MeusAgendamentosPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState<number | null>(null);
  const [error, setError] = useState('');

  const loadAgendamentos = async () => {
    try {
      const data = await apiFetch<Agendamento[]>('/api/agendamentos/meus');
      setAgendamentos(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar agendamentos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
      return;
    }
    if (user) {
      loadAgendamentos();
    }
  }, [user, authLoading]);

  const handleCancelar = async (id: number) => {
    if (!confirm('Tem certeza que deseja cancelar este agendamento?')) return;

    setCancellingId(id);
    try {
      await apiFetch(`/api/agendamentos/${id}/cancelar`, {
        method: 'PATCH',
      });
      await loadAgendamentos();
    } catch (err: any) {
      alert(err.message || 'Erro ao cancelar agendamento.');
    } finally {
      setCancellingId(null);
    }
  };

  const formatDate = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleDateString('pt-BR', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  if (authLoading || loading) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-slate-400">
        Carregando seus agendamentos...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <Calendar className="w-7 h-7 text-brand-400" />
            Meus Agendamentos
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Acompanhe o histórico e o status dos seus horários agendados
          </p>
        </div>
        <Link
          href="/agendar"
          className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-pink-600 hover:from-brand-500 hover:to-pink-500 rounded-xl shadow-md transition-all self-start sm:self-auto"
        >
          Novo Agendamento
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {agendamentos.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-3xl space-y-4">
          <Calendar className="w-12 h-12 mx-auto text-slate-600" />
          <h3 className="text-lg font-bold text-white">Nenhum agendamento encontrado</h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto">
            Você ainda não realizou nenhum agendamento. Que tal escolher um serviço agora?
          </p>
          <Link
            href="/agendar"
            className="inline-block px-6 py-3 text-sm font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-500 transition-colors"
          >
            Agendar Agora
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {agendamentos.map((ag) => {
            const isCancelled = ag.status === 'CANCELADO';
            return (
              <div
                key={ag.id}
                className={`p-6 rounded-2xl border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 ${
                  isCancelled
                    ? 'bg-slate-950/50 border-slate-800/60 opacity-60'
                    : 'bg-slate-900/90 border-slate-800 hover:border-slate-700 shadow-md'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                        isCancelled
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}
                    >
                      {ag.status}
                    </span>
                    <span className="text-xs text-slate-400">
                      ID: #{ag.id}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white">
                    {ag.servico?.nome || 'Serviço do Salão'}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-4 h-4 text-brand-400" />
                      {formatDate(ag.data_hora_inicio)}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-brand-400" />
                      {formatTime(ag.data_hora_inicio)} - {formatTime(ag.data_hora_fim)}
                    </span>
                    {ag.funcionario && (
                      <span className="flex items-center gap-1.5 text-slate-400">
                        <UserCheck className="w-4 h-4 text-purple-400" />
                        {ag.funcionario.nome}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end border-t sm:border-t-0 pt-4 sm:pt-0 border-slate-800">
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Preço</span>
                    <span className="text-lg font-bold text-white">
                      R$ {(ag.servico?.preco || 0).toFixed(2)}
                    </span>
                  </div>

                  {!isCancelled && (
                    <button
                      onClick={() => handleCancelar(ag.id)}
                      disabled={cancellingId === ag.id}
                      className="px-4 py-2 text-xs font-semibold text-rose-300 hover:text-white bg-rose-500/10 hover:bg-rose-600 rounded-xl border border-rose-500/20 transition-all flex items-center gap-1.5"
                    >
                      <XCircle className="w-4 h-4" />
                      {cancellingId === ag.id ? 'Cancelando...' : 'Cancelar'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
