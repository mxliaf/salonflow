'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';
import { Sparkles, Clock, DollarSign, ArrowRight, ShieldCheck, CalendarCheck } from 'lucide-react';

interface Servico {
  id: number;
  nome: string;
  descricao: string;
  duracao_minutos: number;
  preco: number;
  ativo: boolean;
}

export default function HomePage() {
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadServicos() {
      try {
        const data = await apiFetch<Servico[]>('/api/servicos');
        setServicos(data);
      } catch (err) {
        console.error('Erro ao carregar serviços:', err);
      } finally {
        setLoading(false);
      }
    }
    loadServicos();
  }, []);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-slate-900 via-slate-800 to-brand-950 p-8 sm:p-12 border border-slate-800 shadow-2xl">
        <div className="max-w-2xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            Experiência Premium de Beleza
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Reserve seu horário em <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-400 to-pink-400">segundos</span>
          </h1>
          <p className="text-lg text-slate-300">
            Escolha o serviço desejado, consulte a disponibilidade em tempo real e garanta seu agendamento no SalonFlow sem filas ou complicações.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <Link
              href="/agendar"
              className="inline-flex items-center gap-2 px-6 py-3.5 text-base font-semibold text-white bg-gradient-to-r from-brand-600 to-pink-600 hover:from-brand-500 hover:to-pink-500 rounded-xl shadow-lg shadow-brand-600/30 transition-all hover:scale-105"
            >
              Agendar Horário
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Differentials */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-brand-500/10 text-brand-400">
            <CalendarCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Disponibilidade em Tempo Real</h3>
            <p className="text-sm text-slate-400 mt-1">Visualize exatamente os horários livres antes de reservar.</p>
          </div>
        </div>
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Atendimento Pontual</h3>
            <p className="text-sm text-slate-400 mt-1">Duração estimada de cada procedimento para seu maior conforto.</p>
          </div>
        </div>
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-4">
          <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Profissionais Qualificados</h3>
            <p className="text-sm text-slate-400 mt-1">Especialistas prontos para realçar o seu melhor estilo.</p>
          </div>
        </div>
      </div>

      {/* Services List */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Nossos Serviços</h2>
            <p className="text-slate-400 text-sm">Selecione um serviço para realizar seu agendamento</p>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 rounded-2xl bg-slate-900 animate-pulse border border-slate-800" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servicos.map((servico) => (
              <div
                key={servico.id}
                className="group relative rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-brand-500/50 p-6 flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:shadow-brand-500/5"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-lg font-bold text-white group-hover:text-brand-300 transition-colors">
                      {servico.nome}
                    </h3>
                    <span className="px-2.5 py-1 rounded-full bg-slate-800 text-brand-400 font-bold text-sm">
                      R$ {servico.preco.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 line-clamp-2">
                    {servico.descricao || 'Serviço profissional de alta qualidade com garantia de satisfação.'}
                  </p>
                </div>

                <div className="pt-6 mt-4 border-t border-slate-800/60 flex items-center justify-between">
                  <span className="flex items-center gap-1 text-xs font-medium text-slate-400">
                    <Clock className="w-4 h-4 text-brand-400" />
                    {servico.duracao_minutos} min
                  </span>
                  <Link
                    href={`/agendar?servicoId=${servico.id}`}
                    className="px-4 py-2 text-xs font-semibold text-white bg-slate-800 group-hover:bg-brand-600 rounded-lg transition-colors flex items-center gap-1"
                  >
                    Agendar
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
