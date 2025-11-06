import React from 'react';
import { useWidgetProps } from 'fastapps';

export default function {ClassName}() {
  const props = useWidgetProps();

  return (
    <div style={{
      background: '#000',
      color: '#fff',
      padding: '40px',
      textAlign: 'center',
      borderRadius: '8px',
      fontFamily: 'monospace'
    }}>
      <h1>{props?.message || 'Welcome to FastApps'}</h1>
    </div>
  );
}
