'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { apiFetch, ApiError } from '@/lib/api';
import { Calendar, Clock, Scissors, UserCheck, AlertCircle, CheckCircle2, ArrowLeft, Sparkles } from 'lucide-react';

interface Servico {
  id: number;
  nome: string;
  descricao: string;
  duracao_minutos: number;
  preco: number;
}

interface Funcionario {
  id: number;
  nome: string;
  email: string;
}

interface SlotDisponivel {
  horario_inicio: string;
  horario_fim: string;
  disponivel: boolean;
}

function AgendarContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isLoading: authLoading } = useAuth();

  const initialServicoId = searchParams.get('servicoId');

  const [servicos, setServicos] = useState<Servico[]>([]);
  const [funcionarios, setFuncionarios] = useState<Funcionario[]>([]);
  const [selectedServico, setSelectedServico] = useState<Servico | null>(null);
  const [selectedFuncionarioId, setSelectedFuncionarioId] = useState<string>('');
  
  // Data inicial (amanhã no formato YYYY-MM-DD)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const defaultDateStr = tomorrow.toISOString().split('T')[0];

  const [selectedDate, setSelectedDate] = useState<string>(defaultDateStr);
  const [slots, setSlots] = useState<SlotDisponivel[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<SlotDisponivel | null>(null);

  const [loadingServicos, setLoadingServicos] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Carregar lista de serviços e funcionários
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [servData, funcData] = await Promise.all([
          apiFetch<Servico[]>('/api/servicos'),
          apiFetch<Funcionario[]>('/api/auth/funcionarios').catch(() => [])
        ]);
        setServicos(servData);
        setFuncionarios(funcData);

        if (initialServicoId) {
          const found = servData.find((s) => s.id === Number(initialServicoId));
          if (found) setSelectedServico(found);
        } else if (servData.length > 0) {
          setSelectedServico(servData[0]);
        }
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      } finally {
        setLoadingServicos(false);
      }
    }
    loadInitialData();
  }, [initialServicoId]);

  // Carregar slots quando serviço, funcionário ou data mudar
  useEffect(() => {
    if (!selectedServico || !selectedDate) return;

    const servicoId = selectedServico.id;

    async function fetchSlots() {
      setLoadingSlots(true);
      setError('');
      setSelectedSlot(null);
      try {
        let url = `/api/agendamentos/disponiveis?data=${selectedDate}&servico_id=${servicoId}`;
        if (selectedFuncionarioId) {
          url += `&funcionario_id=${selectedFuncionarioId}`;
        }
        const data = await apiFetch<SlotDisponivel[]>(url);
        setSlots(data);
      } catch (err: any) {
        setError('Erro ao carregar horários disponíveis');
      } finally {
        setLoadingSlots(false);
      }
    }

    fetchSlots();
  }, [selectedServico, selectedFuncionarioId, selectedDate]);

  const handleConfirmBooking = async () => {
    if (!user) {
      router.push('/login');
      return;
    }

    if (!selectedServico || !selectedSlot) {
      setError('Por favor selecione um serviço e um horário.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await apiFetch('/api/agendamentos', {
        method: 'POST',
        body: JSON.stringify({
          servico_id: selectedServico.id,
          funcionario_id: selectedFuncionarioId ? Number(selectedFuncionarioId) : null,
          data_hora_inicio: selectedSlot.horario_inicio
        })
      });

      setSuccess(true);
      setTimeout(() => {
        router.push('/meus-agendamentos');
      }, 1500);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 409) {
        setError('Ops! Este horário acabou de ser reservado por outro cliente. Por favor, escolha outro slot.');
      } else {
        setError(err.message || 'Erro ao realizar agendamento.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  if (loadingServicos || authLoading) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-slate-400">
        Carregando opções de agendamento...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <Sparkles className="w-7 h-7 text-brand-400" />
            Agendar Horário
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Escolha o serviço, a data e o horário de sua preferência
          </p>
        </div>
      </div>

      {success && (
        <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-4 animate-fadeIn">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
          <div>
            <h3 className="font-bold text-lg text-emerald-200">Agendamento Confirmado!</h3>
            <p className="text-sm text-emerald-300/90">Redirecionando para a lista de seus agendamentos...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulário de Seleção (2 Colunas) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Passo 1: Selecionar Serviço */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Scissors className="w-5 h-5 text-brand-400" />
              1. Selecione o Serviço
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {servicos.map((serv) => {
                const isSelected = selectedServico?.id === serv.id;
                return (
                  <button
                    key={serv.id}
                    onClick={() => setSelectedServico(serv)}
                    className={`p-4 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-brand-600/15 border-brand-500 text-white shadow-md'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-semibold text-sm">{serv.nome}</div>
                    <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-brand-400" />
                        {serv.duracao_minutos} min
                      </span>
                      <span className="font-bold text-brand-300">R$ {serv.preco.toFixed(2)}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Passo 2: Profissional e Data */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-brand-400" />
              2. Escolha o Profissional e a Data
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Profissional (Opcional)
                </label>
                <select
                  value={selectedFuncionarioId}
                  onChange={(e) => setSelectedFuncionarioId(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-brand-500"
                >
                  <option value="">Qualquer profissional disponível</option>
                  {funcionarios.map((func) => (
                    <option key={func.id} value={func.id}>
                      {func.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Data do Agendamento
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>
          </div>

          {/* Passo 3: Horários Disponíveis */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-brand-400" />
              3. Horários Disponíveis
            </h2>

            {loadingSlots ? (
              <div className="py-8 text-center text-slate-400 text-sm">
                Buscando horários disponíveis...
              </div>
            ) : slots.length === 0 ? (
              <div className="py-8 text-center text-slate-400 text-sm">
                Nenhum horário disponível para a data selecionada.
              </div>
            ) : (
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2.5">
                {slots.map((slot, index) => {
                  const isSelected = selectedSlot?.horario_inicio === slot.horario_inicio;
                  return (
                    <button
                      key={index}
                      disabled={!slot.disponivel}
                      onClick={() => setSelectedSlot(slot)}
                      className={`py-2.5 px-2 rounded-xl text-xs font-semibold border transition-all text-center ${
                        !slot.disponivel
                          ? 'bg-slate-950/40 border-slate-800/40 text-slate-600 cursor-not-allowed line-through'
                          : isSelected
                          ? 'bg-gradient-to-r from-brand-600 to-pink-600 border-brand-400 text-white shadow-md shadow-brand-500/20 scale-105'
                          : 'bg-slate-950 border-slate-800 text-slate-200 hover:border-brand-500/50 hover:text-white'
                      }`}
                    >
                      {formatTime(slot.horario_inicio)}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Resumo do Agendamento (1 Coluna) */}
        <div className="space-y-6">
          <div className="sticky top-24 p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
            <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-3">
              Resumo da Reserva
            </h3>

            {selectedServico ? (
              <div className="space-y-4 text-sm">
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Serviço
                  </span>
                  <p className="font-bold text-white text-base">{selectedServico.nome}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{selectedServico.duracao_minutos} minutos</p>
                </div>

                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Data e Horário
                  </span>
                  <p className="font-medium text-slate-200">
                    {selectedDate ? new Date(selectedDate + 'T00:00:00').toLocaleDateString('pt-BR') : '-'}
                  </p>
                  <p className="font-bold text-brand-400 text-base">
                    {selectedSlot ? `${formatTime(selectedSlot.horario_inicio)} - ${formatTime(selectedSlot.horario_fim)}` : 'Selecione um horário'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="font-semibold text-slate-300">Valor Total</span>
                  <span className="text-xl font-extrabold text-white">
                    R$ {selectedServico.preco.toFixed(2)}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Nenhum serviço selecionado</p>
            )}

            <button
              onClick={handleConfirmBooking}
              disabled={!selectedSlot || submitting || success}
              className="w-full py-4 px-4 bg-gradient-to-r from-brand-600 to-pink-600 hover:from-brand-500 hover:to-pink-500 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg shadow-brand-600/30 transition-all flex items-center justify-center gap-2"
            >
              {submitting
                ? 'Confirmando...'
                : !user
                ? 'Fazer Login para Agendar'
                : 'Confirmar Reserva'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AgendarPage() {
  return (
    <Suspense fallback={<div className="max-w-4xl mx-auto py-12 text-center text-slate-400">Carregando...</div>}>
      <AgendarContent />
    </Suspense>
  );
}