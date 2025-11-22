import React, { useState } from 'react';

export default function SQLEditor({ tenantId }){
  const [sql, setSql] = useState('SELECT date, region, revenue FROM sales_summary');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () =>{
    setLoading(true);
    try{
      const resp = await fetch('http://localhost:8000/sql/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Tenant-ID': tenantId },
        body: JSON.stringify({ sql })
      });
      const data = await resp.json();
      setResult(data);
    }catch(e){
      setResult({ error: e.message });
    }finally{ setLoading(false); }
  }

  return (
    <div style={{ padding: 12, border: '1px solid #eee', borderRadius: 8, background:'#fff' }}>
      <h3>SQL Editor</h3>
      <textarea value={sql} onChange={e=>setSql(e.target.value)} style={{ width:'100%', height:120 }} />
      <div style={{ marginTop:8 }}>
        <button onClick={run} disabled={loading}>Run</button>
      </div>
      {result && <pre style={{ marginTop:12, maxHeight:200, overflow:'auto' }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
