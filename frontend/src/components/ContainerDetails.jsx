import React from 'react';
import HealthBadge from './HealthBadge';
import ResourceBar from './ResourceBar';

export default function ContainerDetails({ container, onClose }) {
  if (!container) return null;

  const isStopped = container.status?.toLowerCase() !== 'running';
  const reasons = Array.isArray(container.reasons) ? container.reasons : [];
  const hasReasons = reasons.length > 0;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-wrap">
            <span className="modal-eyebrow">Container Inspection</span>
            <h2 className="modal-title">{container.name}</h2>
          </div>
          <button
            type="button"
            className="btn-close-modal"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Quick Stats Grid */}
          <div className="modal-stats-grid">
            <div className="modal-stat-card">
              <span className="stat-label">Health Status</span>
              <div className="stat-value-box">
                <HealthBadge health={container.health} size="md" />
              </div>
            </div>

            <div className="modal-stat-card">
              <span className="stat-label">Docker Status</span>
              <div className="stat-value-box">
                <span className={`status-pill pill-${isStopped ? 'stopped' : 'running'}`}>
                  {container.status || 'unknown'}
                </span>
              </div>
            </div>

            <div className="modal-stat-card">
              <span className="stat-label">Container ID</span>
              <div className="stat-value-box">
                <code className="code-id">{container.id}</code>
              </div>
            </div>

            <div className="modal-stat-card">
              <span className="stat-label">Total Restarts</span>
              <div className="stat-value-box">
                <span className={`restarts-count ${container.restarts > 0 ? 'has-restarts' : ''}`}>
                  {container.restarts}
                </span>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="modal-section">
            <h3 className="section-title">Resource Utilization</h3>
            <div className="modal-resources">
              <div className="resource-card">
                <ResourceBar
                  label="CPU Utilization"
                  value={container.cpu}
                  isStopped={isStopped}
                />
                <span className="threshold-hint">Warning: &ge;70% | Critical: &gt;85%</span>
              </div>
              <div className="resource-card">
                <ResourceBar
                  label="Memory Utilization"
                  value={container.memory}
                  isStopped={isStopped}
                />
                <span className="threshold-hint">Warning: &ge;70% | Critical: &gt;85%</span>
              </div>
            </div>
          </div>

          {/* Health Evaluation & Alert Reasons */}
          <div className="modal-section">
            <h3 className="section-title">Health Analysis & Alert Reasons</h3>
            {hasReasons ? (
              <div className={`alerts-box alerts-${container.health?.toLowerCase() || 'warning'}`}>
                <div className="alerts-box-header">
                  <svg className="alerts-box-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                  </svg>
                  <span>Detected {reasons.length} issue(s) triggering {container.health} status:</span>
                </div>
                <ul className="alerts-list">
                  {reasons.map((reason, index) => (
                    <li key={index} className="alert-item">
                      <span className="bullet-point">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="alerts-box alerts-healthy">
                <svg className="alerts-box-icon text-emerald" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                </svg>
                <span>Operating normally. No health warnings or failure conditions detected.</span>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
