function Inicio() {
  const centros = [
    { nombre: "Centro Principal", tipo: "Centro de acopio", cantidad: 4250, humedad: 7.9 },
    { nombre: "Centro Norte", tipo: "Centro de acopio", cantidad: 3100, humedad: 8.3 },
  ];
  const proveedores = [
    { nombre: "Juan Pérez", tipo: "Proveedor directo", cantidad: 920, humedad: 8.1 },
    { nombre: "Asoc. San Miguel", tipo: "Proveedor directo", cantidad: 1150, humedad: 7.8 },
  ];
  const exportadoras = [
    { nombre: "Agroarriba", contrato: "Cacao fino de aroma", volumen: 1500 },
    { nombre: "Ecuacacao", contrato: "Contrato NY Dic-25", volumen: 800 },
  ];

  const dataTendencia = [
    { fecha: "Oct 1", precio: 3390 },
    { fecha: "Oct 5", precio: 3420 },
    { fecha: "Oct 10", precio: 3455 },
    { fecha: "Oct 15", precio: 3490 },
    { fecha: "Oct 20", precio: 3470 },
    { fecha: "Oct 25", precio: 3480 },
  ];

  return (
    <div className="space-y-5">
      {/* CARD: Tendencia NY */}
      <div className="bg-gradient-to-br from-emerald-600 to-emerald-400 text-white rounded-3xl p-5 shadow-lg mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <TrendingUp size={22} />
            <h2 className="font-semibold text-sm">Tendencia del cacao NY</h2>
          </div>
          <button className="text-xs bg-white/20 hover:bg-white/30 px-2 py-1 rounded-lg">
            Actualizar
          </button>
        </div>

        <div className="h-28 bg-white/10 rounded-2xl overflow-hidden">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dataTendencia}>
              <XAxis dataKey="fecha" stroke="#ffffff80" tick={{ fontSize: 10 }} />
              <YAxis hide />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255,255,255,0.9)",
                  border: "none",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Line
                type="monotone"
                dataKey="precio"
                stroke="#ffffff"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 flex justify-between text-xs">
          <div>
            <span className="opacity-80">Precio actual:</span>
            <div className="text-lg font-bold">$3,480 / TM</div>
          </div>
          <div className="text-right">
            <span className="opacity-80">Contrato activo:</span>
            <div className="text-sm font-semibold">Dic-25 • +1.2%</div>
          </div>
        </div>
      </div>

      {/* DEMANDA DE EXPORTADORAS */}
      <section className="bg-white rounded-2xl border border-slate-100 p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold">Demanda de exportadoras</div>
          <button className="text-xs text-emerald-600">Ver contratos</button>
        </div>
        <div className="space-y-2">
          {exportadoras.map((e) => (
            <div
              key={e.nombre}
              className="bg-white rounded-2xl border border-slate-100 p-4 flex items-center justify-between hover:shadow-sm transition"
            >
              <div className="flex items-center gap-2">
                <Factory className="text-emerald-600" size={18} />
                <div>
                  <div className="font-semibold text-sm">{e.nombre}</div>
                  <div className="text-xs text-slate-500">{e.contrato}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xl font-semibold text-emerald-700">{e.volumen} TM</div>
                <div className="text-[11px] text-slate-400">Volumen mensual</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CENTROS DE ACOPIO */}
      <section className="bg-white rounded-2xl border border-slate-100 p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold">Centros de acopio</div>
          <button className="text-xs text-emerald-600">Ver todo</button>
        </div>
        <div className="space-y-2">
          {centros.map((c) => (
            <div
              key={c.nombre}
              className="bg-white rounded-2xl border border-slate-100 p-4 flex items-center justify-between hover:shadow-sm transition"
            >
              <div>
                <div className="font-semibold text-sm">{c.nombre}</div>
                <div className="text-xs text-slate-500">{c.tipo}</div>
              </div>
              <div className="text-right">
                <div className="text-xl font-semibold text-emerald-700">{c.cantidad} kg</div>
                <div className="text-[11px] text-slate-400">{c.humedad}% H</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* PROVEEDORES DIRECTOS */}
      <section className="bg-white rounded-2xl border border-slate-100 p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold">Proveedores directos</div>
          <button className="text-xs text-emerald-600">Ver todo</button>
        </div>
        <div className="space-y-2">
          {proveedores.map((p) => (
            <div
              key={p.nombre}
              className="bg-white rounded-2xl border border-slate-100 p-4 flex items-center justify-between hover:shadow-sm transition"
            >
              <div>
                <div className="font-semibold text-sm">{p.nombre}</div>
                <div className="text-xs text-slate-500">{p.tipo}</div>
              </div>
              <div className="text-right">
                <div className="text-xl font-semibold text-emerald-700">{p.cantidad} kg</div>
                <div className="text-[11px] text-slate-400">{p.humedad}% H</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}