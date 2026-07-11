import { useState, useRef, useEffect } from 'react';
import '../components/agentes/agente.scss';

const LUMEN_URL = import.meta.env.VITE_LUMEN_URL || 'http://localhost:5001';
const OPERIS_URL = import.meta.env.VITE_OPERIS_URL || 'http://localhost:5002';

const SUGERENCIAS = [
  '¿Cuántos eventos hay confirmados?',
  '¿Qué eventos hay en total?',
  'Dame el contexto del Tech Summit 2026',
];

const BRIEFING_EJEMPLO = `Buenas tardes, soy Laura Martínez, responsable de marketing de TechCorp S.L. Queremos organizar el Congreso Anual de Innovación Digital en Madrid los días 15, 16 y 17 de octubre de 2026, para unas 350 personas. Necesitamos catering, audiovisuales y streaming. El presupuesto aproximado es de 45.000 euros. Contacto: laura.martinez@techcorp.es · 600 123 456.`;

const BLOQUES_OPERIS = {
  evento: 'Evento',
  cliente: 'Cliente',
  espacio: 'Espacio',
  sala: 'Sala',
  presupuesto: 'Presupuesto',
};

export const AgentePage = () => {
  // ---- estado del chat Lumen ----
  const [mensajes, setMensajes] = useState([
    { de: 'sistema', texto: 'Pregunta a Lumen sobre los eventos. Responde con los datos reales de la base de datos.' },
  ]);
  const [pregunta, setPregunta] = useState('');
  const [pensando, setPensando] = useState(false);
  const sesionId = useRef(null);
  const finHilo = useRef(null);

  // ---- estado de Operis ----
  const [briefing, setBriefing] = useState(BRIEFING_EJEMPLO);
  const [extrayendo, setExtrayendo] = useState(false);
  const [propuesta, setPropuesta] = useState(null);
  const [errorOperis, setErrorOperis] = useState(null);

  // ---- disponibilidad de los agentes ----
  const [servicios, setServicios] = useState({ lumen: null, operis: null });

  useEffect(() => {
    const comprobar = async () => {
      const ping = async (url) => {
        try {
          const r = await fetch(url + '/', { signal: AbortSignal.timeout(2500) });
          return r.ok;
        } catch {
          return false;
        }
      };
      setServicios({ lumen: await ping(LUMEN_URL), operis: await ping(OPERIS_URL) });
    };
    comprobar();
    const intervalo = setInterval(comprobar, 10000);
    return () => clearInterval(intervalo);
  }, []);

  useEffect(() => {
    finHilo.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes]);

  const preguntarLumen = async (texto) => {
    const limpio = texto.trim();
    if (!limpio || pensando) return;
    setMensajes((m) => [...m, { de: 'yo', texto: limpio }]);
    setPregunta('');
    setPensando(true);
    try {
      const cuerpo = sesionId.current
        ? { pregunta: limpio, sesion_id: sesionId.current }
        : { pregunta: limpio };
      const r = await fetch(`${LUMEN_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cuerpo),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.mensaje || `error ${r.status}`);
      sesionId.current = data.sesion_id || sesionId.current;
      setMensajes((m) => [
        ...m,
        {
          de: 'agente',
          texto: data.resumen || '(respuesta sin resumen)',
          validacion: data.requiere_validacion_humana,
        },
      ]);
    } catch (err) {
      setMensajes((m) => [
        ...m,
        { de: 'sistema', texto: `No llego a Lumen (${LUMEN_URL}). ¿Está arrancado su servidor? — ${err.message}` },
      ]);
    } finally {
      setPensando(false);
    }
  };

  const nuevaConversacion = async () => {
    if (sesionId.current) {
      try {
        await fetch(`${LUMEN_URL}/chat/reset`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sesion_id: sesionId.current }),
        });
      } catch {
        /* si Lumen no está, simplemente empezamos de cero en el cliente */
      }
    }
    sesionId.current = null;
    setMensajes([{ de: 'sistema', texto: 'Conversación nueva. La memoria anterior se ha olvidado.' }]);
  };

  const extraerBriefing = async () => {
    if (!briefing.trim() || extrayendo) return;
    setExtrayendo(true);
    setPropuesta(null);
    setErrorOperis(null);
    try {
      const r = await fetch(`${OPERIS_URL}/autocompletar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto_briefing: briefing, motor: 'reglas' }),
      });
      const data = await r.json();
      if (!r.ok || !data.ok) throw new Error(data.resumen || data.mensaje || `error ${r.status}`);
      setPropuesta(data);
    } catch (err) {
      setErrorOperis(`No se pudo extraer el briefing — ${err.message}`);
    } finally {
      setExtrayendo(false);
    }
  };

  return (
    <main className="agente-page">
      <header className="agente-cabecera">
        <h1>Agentes</h1>
        <p>El copiloto Lumen y el autocompletado Operis, conectados a los datos reales.</p>
        <div className="agente-servicios">
          <span className={`servicio ${servicios.lumen === null ? '' : servicios.lumen ? 'on' : 'off'}`}>
            Lumen {servicios.lumen === false && '(apagado)'}
          </span>
          <span className={`servicio ${servicios.operis === null ? '' : servicios.operis ? 'on' : 'off'}`}>
            Operis {servicios.operis === false && '(apagado)'}
          </span>
        </div>
      </header>

      <div className="agente-columnas">
        {/* ================= LUMEN ================= */}
        <section className="agente-tarjeta">
          <h2>💬 Pregunta a Lumen</h2>
          <div className="chat-hilo">
            {mensajes.map((m, i) => (
              <div key={i} className={`chat-msg ${m.de}`}>
                {m.texto}
                {m.validacion && <span className="chat-meta">requiere validación humana</span>}
              </div>
            ))}
            {pensando && <div className="chat-msg sistema">Lumen está pensando…</div>}
            <div ref={finHilo} />
          </div>
          <div className="chat-sugerencias">
            {SUGERENCIAS.map((s) => (
              <button key={s} type="button" onClick={() => preguntarLumen(s)}>{s}</button>
            ))}
            <button type="button" className="reset" onClick={nuevaConversacion}>Nueva conversación</button>
          </div>
          <form
            className="chat-entrada"
            onSubmit={(e) => {
              e.preventDefault();
              preguntarLumen(pregunta);
            }}
          >
            <input
              type="text"
              value={pregunta}
              onChange={(e) => setPregunta(e.target.value)}
              placeholder="Escribe tu pregunta…"
              aria-label="Pregunta para Lumen"
            />
            <button type="submit" disabled={pensando || !pregunta.trim()}>Enviar</button>
          </form>
        </section>

        {/* ================= OPERIS ================= */}
        <section className="agente-tarjeta">
          <h2>📋 Autocompletar briefing con Operis</h2>
          <label className="operis-etiqueta" htmlFor="briefing">
            Pega el email o briefing del cliente:
          </label>
          <textarea
            id="briefing"
            value={briefing}
            onChange={(e) => setBriefing(e.target.value)}
            rows={7}
          />
          <div className="operis-acciones">
            <button type="button" onClick={extraerBriefing} disabled={extrayendo || !briefing.trim()}>
              {extrayendo ? 'Extrayendo…' : 'Autocompletar campos'}
            </button>
          </div>

          {errorOperis && <p className="operis-error">{errorOperis}</p>}

          {propuesta && (
            <div className="operis-resultado">
              {propuesta.requiere_validacion_humana && (
                <p className="operis-aviso">
                  ⚠️ Propuesta del agente — revísala antes de guardar. La IA propone, el humano decide.
                </p>
              )}
              {propuesta.bloqueos_detectados?.length > 0 && (
                <div className="operis-faltan">
                  {propuesta.bloqueos_detectados.map((b) => (
                    <span key={b}>falta: {b}</span>
                  ))}
                </div>
              )}
              <div className="operis-bloques">
                {Object.entries(BLOQUES_OPERIS).map(([clave, titulo]) => {
                  const bloque = propuesta.datos_detectados?.[clave];
                  if (!bloque) return null;
                  return (
                    <div key={clave} className="operis-bloque">
                      <h3>{titulo}</h3>
                      {Object.entries(bloque).map(([k, v]) => (
                        <div key={k} className="operis-campo">
                          <span className="k">{k.replaceAll('_', ' ')}</span>
                          <span className={`v ${v === '' || v === null ? 'vacio' : ''}`}>
                            {v === '' || v === null ? '—' : String(v)}
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
};
