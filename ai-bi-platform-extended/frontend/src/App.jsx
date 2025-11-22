import React, { useEffect, useState } from 'react';
import SQLEditor from './SQLEditor';
import TrainPanel from './TrainPanel';
import AuthStub from './AuthStub';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from "recharts";

function isTimeSeries(data) {
  if (!Array.isArray(data) || data.length === 0) return false;
  const first = data[0];
  return 'date' in first && ('revenue' in first || 'value' in first);
}

export default function App(){
  const [metrics, setMetrics] = useState([]);
  const [nlq, setNlq] = useState('Show me Q3 sales trends');
  const [nlqResult, setNlqResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/dashboard");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setMetrics((m) => [data, ...m].slice(0, 50));
    };
    return () => ws.close();
  }, []);

  const runNlq = async () => {
    setLoading(true);
    setNlqResult(null);
    try {
      const resp = await fetch('http://localhost:8000/nlq', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: nlq })
      });
      const data = await resp.json();
      setNlqResult(data);
    } catch (e) {
      setNlqResult({ error: e.message });
    } finally {
      setLoading(false);
    }
  }

  const chartData = (nlqResult && nlqResult.data && isTimeSeries(nlqResult.data))
    ? nlqResult.data.map(r => ({
        date: r.date ? r.date.slice(0,10) : (r.ts || ""),
        revenue: Number(r.revenue ?? r.value ?? 0)
      }))
    : null;

  const tenantId = 1; // demo default

  return (
    <div style={{ padding: 24, fontFamily: 'Inter, sans-serif' }}>
      <AuthStub />
      <h1 style={{ fontSize: 24, marginBottom: 12 }}>AI-Powered BI — Multi-tenant</h1>

      <section style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>Natural Language Query</h2>
        <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
          <input value={nlq} onChange={e => setNlq(e.target.value)} style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ccc' }} />
          <button onClick={runNlq} disabled={loading} style={{ padding: '8px 12px', borderRadius: 6 }}>{loading ? 'Running…' : 'Run'}</button>
        </div>

        {nlqResult && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 16 }}>
            <div>
              <h3 style={{ marginBottom: 8 }}>NLQ Response (raw)</h3>
              <pre style={{ background: '#fff', padding: 12, borderRadius: 8, border: '1px solid #eee', maxHeight: 320, overflow: 'auto' }}>
                {JSON.stringify(nlqResult, null, 2)}
              </pre>
            </div>

            <div>
              <h3 style={{ marginBottom: 8 }}>Visualization</h3>
              {chartData ? (
                <div style={{ width: '100%', height: 300, background: '#fff', padding: 8, borderRadius: 8, border: '1px solid #eee' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} dot />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ padding: 12, borderRadius: 8, border: '1px dashed #ddd', background: '#fafafa' }}>
                  <em>No time-series data recognized.</em>
                </div>
              )}
            </div>
          </div>
        )}
      </section>

      <div style={{ display:'grid', gridTemplateColumns: '1fr 420px', gap: 16 }}>
        <div>
          <SQLEditor tenantId={tenantId} />
          <div style={{ height:16 }} />
          <TrainPanel />
        </div>
        <div>
          <h2>Real-time Metrics</h2>
          {metrics.map((m, idx) => (
            <div key={idx} style={{ padding: 8, border: '1px solid #ddd', borderRadius: 8, marginBottom: 8 }}>
              <strong>{m.metric}</strong>: {m.value.toFixed(2)} <span style={{ color: '#666' }}>({m.ts})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
