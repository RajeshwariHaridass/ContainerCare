import React from 'react';

export default function HealthBadge({ health, size = 'sm' }) {
  const normalized = (health || 'UNKNOWN').toUpperCase();

  const config = {
    HEALTHY: {
      label: 'HEALTHY',
      className: 'badge-healthy',
      icon: (
        <svg className="badge-icon" viewBox="0 0 16 16" fill="currentColor">
          <path fillRule="evenodd" d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/>
        </svg>
      ),
    },
    WARNING: {
      label: 'WARNING',
      className: 'badge-warning',
      icon: (
        <svg className="badge-icon" viewBox="0 0 16 16" fill="currentColor">
          <path fillRule="evenodd" d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"/>
        </svg>
      ),
    },
    CRITICAL: {
      label: 'CRITICAL',
      className: 'badge-critical',
      icon: (
        <svg className="badge-icon" viewBox="0 0 16 16" fill="currentColor">
          <path fillRule="evenodd" d="M2.343 13.657A8 8 0 1 1 13.657 2.343 8 8 0 0 1 2.343 13.657ZM6.03 4.97a.75.75 0 0 0-1.06 1.06L6.94 8 4.97 9.97a.75.75 0 1 0 1.06 1.06L8 9.06l1.97 1.97a.75.75 0 1 0 1.06-1.06L9.06 8l1.97-1.97a.75.75 0 1 0-1.06-1.06L8 6.94 6.03 4.97Z"/>
        </svg>
      ),
    },
    FAILED: {
      label: 'FAILED',
      className: 'badge-failed',
      icon: (
        <svg className="badge-icon" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11 1.75V3h2.25a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1 0-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75ZM4.496 6.675l.66 6.6a2.25 2.25 0 0 0 2.24 2.025h1.208a2.25 2.25 0 0 0 2.24-2.025l.66-6.6a.75.75 0 0 0-1.492-.15l-.66 6.6a.75.75 0 0 1-.748.675H8.596a.75.75 0 0 1-.748-.675l-.66-6.6a.75.75 0 0 0-1.492.15Z"/>
        </svg>
      ),
    },
  };

  const current = config[normalized] || {
    label: normalized,
    className: 'badge-unknown',
    icon: null,
  };

  return (
    <span className={`health-badge ${current.className} ${size === 'md' ? 'badge-md' : 'badge-sm'}`}>
      <span className="badge-dot"></span>
      {current.icon}
      <span className="badge-text">{current.label}</span>
    </span>
  );
}
