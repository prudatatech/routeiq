
import { Cpu, BarChart } from 'lucide-react';
import { AIInsightCard } from '../components/dashboard/AIInsightCard';

export default function AIHubPage() {
  return (
    <div className="space-y-8 pb-12">
      {/* Header with Pulse Animation */}
      <div className="relative p-10 rounded-[2.5rem] bg-white border border-slate-200 overflow-hidden shadow-sm">
        <div className="absolute top-0 right-0 p-8">
          <Cpu className="w-24 h-24 text-yellow-500/20 animate-pulse" />
        </div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <span className="px-4 py-1.5 rounded-full bg-yellow-500 text-black text-[10px] font-black tracking-[0.2em] uppercase shadow-[0_4px_20px_rgba(249,201,53,0.4)]">
              Phase 4 Active
            </span>
            <div className="flex gap-1">
              {[1, 2, 3].map(i => (
                <div key={i} className="w-1.5 h-1.5 rounded-full bg-yellow-500/40 animate-ping" style={{ animationDelay: `${i * 200}ms` }} />
              ))}
            </div>
          </div>
          
          <h1 className="text-6xl font-black text-slate-900 font-space tracking-tighter uppercase mb-4 leading-[0.9]">
            AI <span className="text-yellow-500">Intelligence</span> Hub
          </h1>
          <p className="max-w-xl text-slate-500 font-medium text-lg leading-relaxed">
            Harnessing neural network optimization to redefine fleet efficiency. Real-time predictive analytics and autonomous route synchronization active.
          </p>
        </div>

        {/* Binary Rain Background (Mock) */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none select-none font-mono text-[10px] text-yellow-600 overflow-hidden leading-none break-all p-4">
          {Array(20).fill('011010101101010010101011010101010110').join(' ')}
        </div>
      </div>

      {/* Primary Intelligence Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AIInsightCard 
          title="Neural Route Synthesis"
          insight="AI has calculated a 14% reduction in fuel consumption by rerouting the northern cluster through secondary corridors."
          score={98.4}
          trend="up"
        />
        <AIInsightCard 
          title="Demand Prediction AI"
          insight="Projecting a 220% surge in delivery requirements for the downtown sector within the next 48 hours."
          score={94.2}
          trend="up"
        />
        <AIInsightCard 
          title="Vehicle Health Logic"
          insight="Proactive alert: Vehicle MH-9003 shows early signs of hydraulic variance. Maintenance advised within 42.4km."
          score={89.1}
          trend="down"
        />
      </div>

      {/* System Status Table */}
      <div className="rounded-[2.5rem] bg-white border border-slate-200 p-8 shadow-sm">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-yellow-400 text-slate-900 shadow-sm border border-yellow-500/20">
              <BarChart className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-black text-slate-900 font-space tracking-tight uppercase">Intelligence Stream</h2>
              <p className="text-slate-500 text-xs font-bold tracking-widest uppercase">Live Process Logs</p>
            </div>
          </div>
          <button className="px-6 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-100 transition-colors uppercase tracking-widest">
            Export Model Data
          </button>
        </div>

        <div className="space-y-4">
          {[
            { tag: 'LOCAL', msg: 'Synchronizing route clusters for zone BX-04...', time: '0.2ms' },
            { tag: 'GLOBAL', msg: 'Calibrating global demand distribution model v2.4', time: '1.4ms' },
            { tag: 'FLEET', msg: 'Predictive maintenance vector applied to vehicle ID #4002', time: '0.8ms' },
          ].map((log, i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-200 group hover:border-yellow-400/50 transition-colors">
              <div className="flex items-center gap-4">
                <span className="font-mono text-[10px] text-yellow-600 font-bold bg-yellow-500/10 px-2 py-0.5 rounded border border-yellow-500/20">
                  {log.tag}
                </span>
                <span className="text-slate-700 font-bold text-sm tracking-tight group-hover:text-slate-900 transition-colors">{log.msg}</span>
              </div>
              <span className="text-slate-400 font-mono text-xs">{log.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
