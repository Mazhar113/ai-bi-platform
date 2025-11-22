import React, { useState } from 'react';

export default function TrainPanel(){
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const train = async () =>{
    setLoading(true);
    setStatus(null);
    try{
      const resp = await fetch('http://localhost:8000/train', { method: 'POST' });
      const data = await resp.json();
      setStatus(data);
    }catch(e){ setStatus({ error: e.message }); }
    finally{ setLoading(false); }
  }

  return (
    <div style={{ padding:12, border:'1px solid #eee', borderRadius:8, background:'#fff' }}>
      <h3>Model Training</h3>
      <p>Train a demo model on current tenant data.</p>
      <button onClick={train} disabled={loading}>{loading? 'Training…':'Start training'}</button>
      {status && <pre style={{ marginTop:12 }}>{JSON.stringify(status, null, 2)}</pre>}
    </div>
  )
}
