import React from 'react';

export default function Header({
  backendStatus,
  isRefreshing,
  onRefresh,
  autoRefresh,
  onToggleAutoRefresh,
  lastUpdated,
  isDemoMode,
  onToggleDemo,
}) {
  const isHealthy = backendStatus === 'online';
  const isChecking = backendStatus === 'checking';
  const isDemo = backendStatus === 'demo' || isDemoMode;

  let statusClass = 'status-offline';
  let statusText = 'Backend Offline';

  if (isDemo) {
    statusClass = 'status-demo';
    statusText = 'Demo Dataset Active';
  } else if (isHealthy) {
    statusClass = 'status-online';
    statusText = 'API Connected';
  } else if (isChecking) {
    statusClass = 'status-checking';
    statusText = 'Checking...';
  } else if (backendStatus === 'docker_unavailable') {
    statusClass = 'status-warning';
    statusText = 'Docker Daemon Unreachable';
  }

  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="brand-logo-container">
          <svg className="brand-logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
            <line x1="12" y1="22.08" x2="12" y2="12" />
          </svg>
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">ContainerCare</h1>
            <span className="brand-badge">DevOps v1.0</span>
          </div>
          <p className="brand-subtitle">Docker Container Health Monitor</p>
        </div>
      </div>

      <div className="header-actions">
        {/* Backend Connectivity Status Pill */}
        <div className={`connection-pill ${statusClass}`} title={`Backend connection: ${statusText}`}>
          <span className="connection-dot" />
          <span className="connection-text">{statusText}</span>
        </div>

        {/* Demo Data Toggle Button */}
        <button
          type="button"
          className={`btn-toggle-demo ${isDemo ? 'is-active' : ''}`}
          onClick={onToggleDemo}
          title={isDemo ? 'Switch to live Docker monitoring' : 'Preview demo sample containers'}
        >
          {isDemo ? 'Live Docker API' : 'Sample Data'}
        </button>

        {/* Auto Refresh Toggle */}
        <label className="auto-refresh-toggle" title="Toggle automatic polling every 10 seconds">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => onToggleAutoRefresh(e.target.checked)}
          />
          <span className="toggle-label">Auto-refresh (10s)</span>
        </label>

        {/* Refresh Button */}
        <button
          type="button"
          className="btn-refresh"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Manual refresh"
        >
          <svg
            className={`refresh-icon ${isRefreshing ? 'is-spinning' : ''}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
          <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>

        {lastUpdated && (
          <span className="last-updated-text">
            Updated: {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>
    </header>
  );
}
