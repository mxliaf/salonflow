import { Scissors } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 text-slate-400 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Scissors className="w-5 h-5 text-brand-500" />
          <span className="font-semibold text-slate-200">SalonFlow</span>
          <span className="text-sm text-slate-500">— Sistema de Agendamentos</span>
        </div>
        <p className="text-xs text-slate-500">
          &copy; {new Date().getFullYear()} SalonFlow. Todos os direitos reservados.
        </p>
      </div>
    </footer>
  );
}
