import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Home, Package, ScanLine, Calculator, User, Settings, TrendingUp, Factory, PlusCircle, Trash2, Clock } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

// ✅ Calculadora mejorada:
// - Spot fijo: 6319 USD/TM
// - Diferenciales dinámicos
// - Historial con botón para borrar

const NavButton = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center gap-1 flex-1 py-2 ${
      active ? "text-emerald-600" : "text-slate-500"
    }`}
  >
    <Icon size={22} />
    <span className="text-[10px] tracking-wide">{label}</span>
  </button>
);

const StatCard = ({ title, value, sub }) => (
  <div className="bg-white rounded-2xl border border-slate-100 p-3">
    <div className="text-xs text-slate-500">{title}</div>
    <div className="text-xl font-semibold leading-tight">{value}</div>
    {sub && <div className="text-[11px] text-slate-400 mt-1">{sub}</div>}
  </div>
);

const dataTendencia = [
  { fecha: "Oct 1", precio: 6120 },
  { fecha: "Oct 5", precio: 6190 },
  { fecha: "Oct 10", precio: 6250 },
  { fecha: "Oct 15", precio: 6295 },
  { fecha: "Oct 20", precio: 6310 },
  { fecha: "Oct 25", precio: 6319 },
];

const CardTendencia = () => (
  <div className="bg-gradient-to-br from-emerald-600 to-emerald-400 text-white rounded-3xl p-5 shadow-lg mb-4">
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        <TrendingUp size={22} />
        <h2 className="font-semibold text-sm">Tendencia del cacao NY</h2>
      </div>
      <button className="text-xs bg-white/20 hover:bg-white/30 px-2 py-1 rounded-lg">Actualizar</button>
    </div>

    <div className="h-28 bg-white/10 rounded-2xl overflow-hidden">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={dataTendencia} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <XAxis dataKey="fecha" stroke="#ffffff80" tick={{ fontSize: 10 }} />
          <YAxis hide domain={[6100, 6400]} />
          <Tooltip contentStyle={{ backgroundColor: 'rgba(255,255,255,0.9)', border: 'none', borderRadius: '8px', fontSize: '12px' }} />
          <Line type="monotone" dataKey="precio" stroke="#ffffff" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>

    <div className="mt-3 flex justify-between text-xs">
      <div>
        <span className="opacity-80">Precio actual:</span>
        <div className="text-lg font-bold">$6,319 / TM</div>
      </div>
      <div className="text-right">
        <span className="opacity-80">Contrato activo:</span>
        <div className="text-sm font-semibold">Dic-25 • +0.9%</div>
      </div>
    </div>
  </div>
);

function Calculadora() {
  const [diferenciales, setDiferenciales] = useState([{ nombre: "Exportadora", valor: 200 }]);
  const [historial, setHistorial] = useState([]);
  const spot = 6319;

  const calcular = (dif) => {
    const tmNeto = spot - dif.valor;
    const qq = tmNeto / 22.0462;
    return { tmNeto, qq };
  };

  const agregarDiferencial = () => {
    setDiferenciales([...diferenciales, { nombre: `Dif-${diferenciales.length + 1}`, valor: 0 }]);
  };

  const eliminarDiferencial = (index) => {
    const nuevos = diferenciales.filter((_, i) => i !== index);
    setDiferenciales(nuevos);
  };

  const guardarHistorial = () => {
    const fecha = new Date().toLocaleString();
    const resultados = diferenciales.map((d) => {
      const calc = calcular(d);
      return { ...d, tmNeto: calc.tmNeto.toFixed(2), qq: calc.qq.toFixed(2) };
    });
    setHistorial([{ fecha, resultados }, ...historial.slice(0, 4)]);
  };

  const borrarHistorial = () => {
    if (confirm('¿Deseas borrar todo el historial de cálculos?')) {
      setHistorial([]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-sm font-semibold">Calculadora de precios según diferenciales</div>

      <div className="bg-white rounded-2xl border border-slate-100 p-4 space-y-3">
        <div className="text-xs text-slate-500">Spot actual: <span className="font-semibold text-emerald-700">$6,319 / TM</span></div>

        {diferenciales.map((d, index) => {
          const { tmNeto, qq } = calcular(d);
          return (
            <div key={index} className="border border-slate-200 rounded-xl p-3">
              <div className="flex justify-between items-center mb-2">
                <input
                  value={d.nombre}
                  onChange={(e) => {
                    const nuevos = [...diferenciales];
                    nuevos[index].nombre = e.target.value;
                    setDiferenciales(nuevos);
                  }}
                  className="font-semibold text-sm w-2/3 bg-transparent border-b border-slate-200 focus:outline-none"
                />
                <button onClick={() => eliminarDiferencial(index)} className="text-slate-400 hover:text-red-500">
                  <Trash2 size={16} />
                </button>
              </div>
              <label className="text-xs text-slate-500">Diferencial (USD/TM)</label>
              <input
                type="number"
                value={d.valor}
                onChange={(e) => {
                  const nuevos = [...diferenciales];
                  nuevos[index].valor = parseFloat(e.target.value) || 0;
                  setDiferenciales(nuevos);
                }}
                className="w-full mt-1 px-3 py-2 rounded-xl border border-slate-200"
              />
              <div className="grid grid-cols-2 gap-3 mt-3">
                <StatCard title="Precio Neto (TM)" value={`$${tmNeto.toFixed(2)}`} />
                <StatCard title="Precio por QQ" value={`$${qq.toFixed(2)}`} sub="División 22.0462" />
              </div>
            </div>
          );
        })}

        <button
          onClick={agregarDiferencial}
          className="w-full mt-2 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm inline-flex items-center justify-center gap-2"
        >
          <PlusCircle size={16} /> Añadir diferencial
        </button>

        <div className="flex gap-2 mt-3">
          <button
            onClick={guardarHistorial}
            className="flex-1 py-2 rounded-xl bg-emerald-600 text-white text-sm font-medium"
          >
            Guardar cálculo
          </button>
          <button
            onClick={borrarHistorial}
            className="px-3 py-2 rounded-xl border text-sm text-slate-600 flex items-center gap-1"
          >
            <Trash2 size={14} /> Borrar historial
          </button>
        </div>
      </div>

      {historial.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-100 p-4">
          <div className="flex items-center justify-between mb-2 text-sm font-semibold">
            <div className="flex items-center gap-2"><Clock size={16} className="text-emerald-600" /> Historial reciente</div>
            <span className="text-xs text-slate-400">({historial.length}) cálculos</span>
          </div>
          <div className="space-y-2 text-xs text-slate-600">
            {historial.map((h, i) => (
              <div key={i} className="border border-slate-100 rounded-xl p-2">
                <div className="text-[11px] text-slate-400 mb-1">{h.fecha}</div>
                {h.resultados.map((r, j) => (
                  <div key={j} className="flex justify-between">
                    <span>{r.nombre}</span>
                    <span>{`$${r.tmNeto} / $${r.qq} qq`}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AppPrototype() {
  const [active, setActive] = useState("calculadora");
  const ActiveComp = Calculadora;

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-emerald-50 to-white text-slate-900">
      <div className="max-w-sm mx-auto py-4 px-3">
        <div className="rounded-[28px] border border-slate-200 shadow-xl bg-white overflow-hidden">
          <div className="px-4 pt-4 pb-3 border-b border-slate-100 bg-white/70 backdrop-blur">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-emerald-600 grid place-items-center text-white text-xs font-bold">CC</div>
                <div>
                  <div className="text-[11px] text-slate-500">Cooperativa</div>
                  <div className="text-sm font-semibold">Coop Cacao</div>
                </div>
              </div>
              <button className="text-slate-500" aria-label="Ajustes">
                <Settings size={18} />
              </button>
            </div>
          </div>

          <div className="h-[640px] overflow-y-auto p-4 bg-slate-50">
            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.18 }}
                className="space-y-4"
              >
                <ActiveComp />
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="border-t border-slate-200 bg-white">
            <div className="flex items-center">
              <NavButton icon={Home} label="Inicio" active={active === "inicio"} onClick={() => setActive("inicio")} />
              <NavButton icon={Calculator} label="Calculadora" active={active === "calculadora"} onClick={() => setActive("calculadora")} />
              <NavButton icon={Package} label="Inventario" />
              <NavButton icon={ScanLine} label="QR" />
              <NavButton icon={User} label="Perfil" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}