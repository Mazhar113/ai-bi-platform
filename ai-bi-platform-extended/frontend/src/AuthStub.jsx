import React from 'react';
export default function AuthStub(){
  return (
    <div style={{ marginBottom: 12 }}>
      <button onClick={()=>alert('Open Keycloak login in a new tab and paste token into settings (demo flow)')}>Login (demo)</button>
    </div>
  )
}
