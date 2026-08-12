'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { apiFetch } from '@/lib/api';
import {
  LayoutDashboard,
  Calendar,
  Plus,
  Radio,
  Scissors,
  User,
  Clock,
  DollarSign,
  AlertCircle,
  XCircle,
  Edit2,
  Trash2,
  Sparkles,
  CheckCircle2
} from 'lucide-react';

interface Servico {
  id: number;
  nome: string;
  descricao: string;
  duracao_minutos: number;
  preco: number;
  ativo: boolean;
}

interface Agendamento {
  id: number;
  data_hora_inicio: string;
  data_hora_fim: string;
  status: 'PENDENTE' | 'CONFIRMADO' | 'CANCELADO';
  cliente?: { id: number; nome: string; email: string };
  funcionario?: { id: number; nome: string };
  servico?: { id: number; nome: string; preco: number; duracao_minutos: number };
}

export default function AdminPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<'agendamentos' | 'servicos'>('agendamentos');
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);

  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [liveNotification, setLiveNotification] = useState<string | null>(null);

  // Form Modal Estado para Serviço
  const [showServiceModal, setShowServiceModal] = useState(false);
  const [editingServiceId, setEditingServiceId] = useState<number | null>(null);
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [duracaoMinutos, setDuracaoMinutos] = useState(60);
  const [preco, setPreco] = useState(100);
  const [submittingService, setSubmittingService] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);

  const loadData = async () => {
    try {
      const [agData, servData] = await Promise.all([
        apiFetch<Agendamento[]>('/api/agendamentos/salao'),
        apiFetch<Servico[]>('/api/servicos?apenas_ativos=false')
      ]);
      setAgendamentos(agData);
      setServicos(servData);
    } catch (err: any) {
      console.error('Erro ao carregar dados do admin:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && (!user || (user.role !== 'ADMIN' && user.role !== 'FUNCIONARIO'))) {
      router.push('/login');
      return;
    }
    if (user) {
      loadData();
    }
  }, [user, authLoading]);

  // Conectar ao WebSocket
  useEffect(() => {
    if (!user) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/agendamentos';
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.event === 'NOVO_AGENDAMENTO') {
          setLiveNotification('Novo agendamento recebido!');
          setAgendamentos((prev) => [message.agendamento, ...prev]);
          setTimeout(() => setLiveNotification(null), 4000);
        } else if (message.event === 'AGENDAMENTO_CANCELADO') {
          setLiveNotification('Um agendamento foi cancelado.');
          setAgendamentos((prev) =>
            prev.map((a) => (a.id === message.agendamento.id ? message.agendamento : a))
          );
          setTimeout(() => setLiveNotification(null), 4000);
        }
      } catch (err) {
        console.error('Erro ao processar mensagem WS:', err);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [user]);

  const handleSaveService = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingService(true);
    try {
      if (editingServiceId) {
        await apiFetch(`/api/servicos/${editingServiceId}`, {
          method: 'PUT',
          body: JSON.stringify({
            nome,
            descricao,
            duracao_minutos: Number(duracaoMinutos),
            preco: Number(preco),
          }),
        });
      } else {
        await apiFetch('/api/servicos', {
          method: 'POST',
          body: JSON.stringify({
            nome,
            descricao,
            duracao_minutos: Number(duracaoMinutos),
            preco: Number(preco),
          }),
        });
      }
      setShowServiceModal(false);
      resetServiceForm();
      await loadData();
    } catch (err: any) {
      alert(err.message || 'Erro ao salvar serviço');
    } finally {
      setSubmittingService(false);
    }
  };

  const handleDeactivateService = async (id: number) => {
    if (!confirm('Deseja desativar este serviço?')) return;
    try {
      await apiFetch(`/api/servicos/${id}`, { method: 'DELETE' });
      await loadData();
    } catch (err: any) {
      alert(err.message || 'Erro ao desativar serviço');
    }
  };

  const handleCancelAgendamento = async (id: number) => {
    if (!confirm('Deseja cancelar este agendamento?')) return;
    try {
      await apiFetch(`/api/agendamentos/${id}/cancelar`, { method: 'PATCH' });
      await loadData();
    } catch (err: any) {
      alert(err.message || 'Erro ao cancelar agendamento');
    }
  };

  const resetServiceForm = () => {
    setEditingServiceId(null);
    setNome('');
    setDescricao('');
    setDuracaoMinutos(60);
    setPreco(100);
  };

  const openEditService = (s: Servico) => {
    setEditingServiceId(s.id);
    setNome(s.nome);
    setDescricao(s.descricao || '');
    setDuracaoMinutos(s.duracao_minutos);
    setPreco(s.preco);
    setShowServiceModal(true);
  };

  if (authLoading || loading) {
    return (
      <div className="max-w-7xl mx-auto py-12 text-center text-slate-400">
        Carregando painel administrativo...
      </div>
    );
  }

  const agendamentosConfirmados = agendamentos.filter((a) => a.status === 'CONFIRMADO');
  const faturamentoTotal = agendamentosConfirmados.reduce((acc, a) => acc + (a.servico?.preco || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header com indicador WebSocket ao vivo */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <LayoutDashboard className="w-7 h-7 text-purple-400" />
            Painel do Salão
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Gestão de agendamentos e catálogo de serviços
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold">
            <span className={`w-2.5 h-2.5 rounded-full ${wsConnected ? 'bg-emerald-500 animate-ping' : 'bg-amber-500'}`} />
            <span className={wsConnected ? 'text-emerald-400' : 'text-amber-400'}>
              {wsConnected ? 'Tempo Real Ativo' : 'Conectando WS...'}
            </span>
          </div>
        </div>
      </div>

      {/* Alerta de notificação em tempo real */}
      {liveNotification && (
        <div className="p-4 rounded-2xl bg-purple-600/20 border border-purple-500/40 text-purple-200 flex items-center justify-between animate-bounce">
          <div className="flex items-center gap-3">
            <Radio className="w-5 h-5 text-purple-400" />
            <span className="font-semibold text-sm">{liveNotification}</span>
          </div>
          <span className="text-xs text-purple-300">Atualizado agora</span>
        </div>
      )}

      {/* Cards de Métricas */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center gap-4">
          <div className="p-4 rounded-xl bg-purple-500/10 text-purple-400">
            <Calendar className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Total de Agendamentos
            </span>
            <p className="text-2xl font-bold text-white mt-1">{agendamentos.length}</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center gap-4">
          <div className="p-4 rounded-xl bg-emerald-500/10 text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Confirmados
            </span>
            <p className="text-2xl font-bold text-white mt-1">{agendamentosConfirmados.length}</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center gap-4">
          <div className="p-4 rounded-xl bg-brand-500/10 text-brand-400">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Faturamento Previsto
            </span>
            <p className="text-2xl font-bold text-white mt-1">
              R$ {faturamentoTotal.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-8">
        <button
          onClick={() => setActiveTab('agendamentos')}
          className={`pb-4 text-sm font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'agendamentos'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Calendar className="w-4 h-4" />
          Todos os Agendamentos ({agendamentos.length})
        </button>
        <button
          onClick={() => setActiveTab('servicos')}
          className={`pb-4 text-sm font-bold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'servicos'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Scissors className="w-4 h-4" />
          Gerenciar Serviços ({servicos.length})
        </button>
      </div>

      {/* Aba de Agendamentos */}
      {activeTab === 'agendamentos' && (
        <div className="space-y-4">
          {agendamentos.length === 0 ? (
            <div className="p-12 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-400">
              Nenhum agendamento registrado ainda.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-slate-400 text-xs font-semibold uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-4">Cliente</th>
                    <th className="p-4">Serviço</th>
                    <th className="p-4">Data / Horário</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {agendamentos.map((ag) => (
                    <tr key={ag.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4">
                        <div className="font-semibold text-white">{ag.cliente?.nome || 'Cliente'}</div>
                        <div className="text-xs text-slate-400">{ag.cliente?.email}</div>
                      </td>
                      <td className="p-4">
                        <div className="font-semibold text-slate-200">{ag.servico?.nome || 'Serviço'}</div>
                        <div className="text-xs text-brand-400 font-medium">
                          R$ {(ag.servico?.preco || 0).toFixed(2)}
                        </div>
                      </td>
                      <td className="p-4">
                        <div>{new Date(ag.data_hora_inicio).toLocaleDateString('pt-BR')}</div>
                        <div className="text-xs text-slate-400">
                          {new Date(ag.data_hora_inicio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })} - {new Date(ag.data_hora_fim).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                            ag.status === 'CONFIRMADO'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}
                        >
                          {ag.status}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        {ag.status !== 'CANCELADO' && (
                          <button
                            onClick={() => handleCancelAgendamento(ag.id)}
                            className="px-3 py-1.5 text-xs font-semibold text-rose-300 hover:text-white bg-rose-500/10 hover:bg-rose-600 rounded-lg transition-colors inline-flex items-center gap-1"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Cancelar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Aba de Serviços */}
      {activeTab === 'servicos' && (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button
              onClick={() => {
                resetServiceForm();
                setShowServiceModal(true);
              }}
              className="px-4 py-2.5 bg-gradient-to-r from-purple-600 to-brand-600 hover:from-purple-500 hover:to-brand-500 text-white text-sm font-semibold rounded-xl shadow-md transition-all flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Novo Serviço
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servicos.map((serv) => (
              <div
                key={serv.id}
                className={`p-6 rounded-2xl border transition-all flex flex-col justify-between ${
                  serv.ativo
                    ? 'bg-slate-900/80 border-slate-800'
                    : 'bg-slate-950/40 border-slate-800/40 opacity-50'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <h3 className="font-bold text-white text-lg">{serv.nome}</h3>
                    <span className="text-sm font-bold text-brand-400">
                      R$ {serv.preco.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{serv.descricao}</p>
                  <span className="inline-block text-xs font-semibold text-slate-400 bg-slate-800 px-2.5 py-1 rounded-md">
                    {serv.duracao_minutos} minutos
                  </span>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-800/60 flex items-center justify-between">
                  <span className={`text-xs font-bold ${serv.ativo ? 'text-emerald-400' : 'text-slate-500'}`}>
                    {serv.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openEditService(serv)}
                      className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg transition-colors"
                      title="Editar"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    {serv.ativo && (
                      <button
                        onClick={() => handleDeactivateService(serv.id)}
                        className="p-2 text-rose-400 hover:text-rose-200 bg-rose-500/10 rounded-lg transition-colors"
                        title="Desativar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de Criação / Edição de Serviço */}
      {showServiceModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white">
                {editingServiceId ? 'Editar Serviço' : 'Novo Serviço'}
              </h3>
              <button
                onClick={() => setShowServiceModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveService} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Nome do Serviço
                </label>
                <input
                  type="text"
                  required
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Descrição
                </label>
                <textarea
                  value={descricao}
                  onChange={(e) => setDescricao(e.target.value)}
                  rows={2}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Duração (min)
                  </label>
                  <input
                    type="number"
                    required
                    min={15}
                    step={15}
                    value={duracaoMinutos}
                    onChange={(e) => setDuracaoMinutos(Number(e.target.value))}
                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Preço (R$)
                  </label>
                  <input
                    type="number"
                    required
                    min={0}
                    step={5}
                    value={preco}
                    onChange={(e) => setPreco(Number(e.target.value))}
                    className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowServiceModal(false)}
                  className="w-1/2 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl text-sm"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={submittingService}
                  className="w-1/2 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-xl text-sm shadow-md"
                >
                  {submittingService ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
