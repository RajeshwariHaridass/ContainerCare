import React from 'react';

export default function ResourceBar({ label, value = 0, isStopped = false }) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
  const clamped = Math.max(0, Math.min(100, numericValue));

  // Determine state based on backend thresholds: Warning >= 70, Critical > 85
  let level = 'normal';
  if (isStopped) {
    level = 'stopped';
  } else if (clamped > 85) {
    level = 'critical';
  } else if (clamped >= 70) {
    level = 'warning';
  }

  return (
    <div className="resource-bar-container">
      <div className="resource-bar-header">
        {label && <span className="resource-bar-label">{label}</span>}
        <span className={`resource-bar-value value-${level}`}>
          {isStopped ? '0.00%' : `${numericValue.toFixed(2)}%`}
        </span>
      </div>
      <div className="resource-bar-track">
        <div
          className={`resource-bar-fill fill-${level}`}
          style={{ width: isStopped ? '0%' : `${clamped}%` }}
        />
      </div>
    </div>
  );
}
