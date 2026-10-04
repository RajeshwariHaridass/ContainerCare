import React from 'react';

export default function MetricCards({ containers, activeFilter, onSelectFilter }) {
  const counts = {
    total: containers.length,
    healthy: containers.filter(c => (c.health || '').toUpperCase() === 'HEALTHY').length,
    warning: containers.filter(c => (c.health || '').toUpperCase() === 'WARNING').length,
    critical: containers.filter(c => (c.health || '').toUpperCase() === 'CRITICAL').length,
    failed: containers.filter(c => (c.health || '').toUpperCase() === 'FAILED').length,
  };

  const cards = [
    {
      id: 'ALL',
      title: 'Total Containers',
      count: counts.total,
      theme: 'card-total',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
          <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
          <line x1="6" y1="6" x2="6.01" y2="6"/>
          <line x1="6" y1="18" x2="6.01" y2="18"/>
        </svg>
      ),
    },
    {
      id: 'HEALTHY',
      title: 'Healthy',
      count: counts.healthy,
      theme: 'card-healthy',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      ),
    },
    {
      id: 'WARNING',
      title: 'Warning',
      count: counts.warning,
      theme: 'card-warning',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      ),
    },
    {
      id: 'CRITICAL',
      title: 'Critical',
      count: counts.critical,
      theme: 'card-critical',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      ),
    },
    {
      id: 'FAILED',
      title: 'Failed',
      count: counts.failed,
      theme: 'card-failed',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      ),
    },
  ];

  return (
    <div className="metric-cards-grid">
      {cards.map(card => {
        const isSelected = activeFilter === card.id;
        return (
          <button
            key={card.id}
            type="button"
            className={`metric-card ${card.theme} ${isSelected ? 'is-active' : ''}`}
            onClick={() => onSelectFilter(card.id)}
            title={`Filter by ${card.title}`}
          >
            <div className="card-top">
              <span className="card-title">{card.title}</span>
              <div className="card-icon">{card.icon}</div>
            </div>
            <div className="card-bottom">
              <span className="card-count">{card.count}</span>
              {isSelected && <span className="card-filter-indicator">Filtered</span>}
            </div>
          </button>
        );
      })}
    </div>
  );
}
