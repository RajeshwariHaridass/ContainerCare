import React from 'react';
import HealthBadge from './HealthBadge';
import ResourceBar from './ResourceBar';

export default function ContainerTable({
  containers,
  searchTerm,
  onSearchChange,
  healthFilter,
  onFilterChange,
  onSelectContainer,
}) {
  const filterOptions = [
    { id: 'ALL', label: 'All Containers' },
    { id: 'HEALTHY', label: 'Healthy' },
    { id: 'WARNING', label: 'Warning' },
    { id: 'CRITICAL', label: 'Critical' },
    { id: 'FAILED', label: 'Failed' },
  ];

  // Apply search query and health status filter
  const filtered = containers.filter((container) => {
    const matchesFilter =
      healthFilter === 'ALL' ||
      (container.health || '').toUpperCase() === healthFilter;

    const query = searchTerm.trim().toLowerCase();
    const matchesSearch =
      !query ||
      (container.name && container.name.toLowerCase().includes(query)) ||
      (container.id && container.id.toLowerCase().includes(query));

    return matchesFilter && matchesSearch;
  });

  return (
    <div className="table-card">
      {/* Table Toolbar */}
      <div className="table-toolbar">
        {/* Search Input */}
        <div className="search-box">
          <svg className="search-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Search by name or container ID..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          {searchTerm && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => onSearchChange('')}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Filter Pills */}
        <div className="filter-group">
          {filterOptions.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`filter-btn ${healthFilter === opt.id ? 'is-active' : ''}`}
              onClick={() => onFilterChange(opt.id)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table Content */}
      <div className="table-container">
        {filtered.length === 0 ? (
          <div className="table-empty-state">
            <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
            </svg>
            <h4 className="empty-title">No Containers Found</h4>
            <p className="empty-desc">
              {containers.length === 0
                ? 'No Docker containers were discovered on your Docker daemon.'
                : 'No containers match your search and filter criteria.'}
            </p>
            {searchTerm || healthFilter !== 'ALL' ? (
              <button
                type="button"
                className="btn-reset-filters"
                onClick={() => {
                  onSearchChange('');
                  onFilterChange('ALL');
                }}
              >
                Reset Filters
              </button>
            ) : null}
          </div>
        ) : (
          <table className="containers-table">
            <thead>
              <tr>
                <th>Container Name</th>
                <th>ID</th>
                <th>Status</th>
                <th>Health Status</th>
                <th>CPU Usage</th>
                <th>Memory Usage</th>
                <th>Restarts</th>
                <th>Alerts & Reasons</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => {
                const isStopped = (c.status || '').toLowerCase() !== 'running';
                const reasons = Array.isArray(c.reasons) ? c.reasons : [];

                return (
                  <tr
                    key={c.id}
                    className="table-row-clickable"
                    onClick={() => onSelectContainer(c)}
                  >
                    {/* Name */}
                    <td className="cell-name">
                      <div className="name-wrapper">
                        <span className="container-name">{c.name}</span>
                      </div>
                    </td>

                    {/* ID */}
                    <td className="cell-id">
                      <code className="code-id">{c.id}</code>
                    </td>

                    {/* Docker Status */}
                    <td className="cell-status">
                      <span className={`status-pill pill-${isStopped ? 'stopped' : 'running'}`}>
                        {c.status || 'unknown'}
                      </span>
                    </td>

                    {/* Health Status */}
                    <td className="cell-health">
                      <HealthBadge health={c.health} />
                    </td>

                    {/* CPU Usage */}
                    <td className="cell-metric">
                      <ResourceBar value={c.cpu} isStopped={isStopped} />
                    </td>

                    {/* Memory Usage */}
                    <td className="cell-metric">
                      <ResourceBar value={c.memory} isStopped={isStopped} />
                    </td>

                    {/* Restarts */}
                    <td className="cell-restarts">
                      <span className={`restarts-badge ${c.restarts > 0 ? 'has-restarts' : ''}`}>
                        {c.restarts}
                      </span>
                    </td>

                    {/* Alerts / Reasons */}
                    <td className="cell-reasons">
                      {reasons.length > 0 ? (
                        <div className="reasons-preview">
                          <span className="reason-tag" title={reasons.join(', ')}>
                            {reasons[0]}
                          </span>
                          {reasons.length > 1 && (
                            <span className="reason-more-badge">
                              +{reasons.length - 1} more
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="reason-none">None (Normal)</span>
                      )}
                    </td>

                    {/* Action */}
                    <td className="cell-action">
                      <button
                        type="button"
                        className="btn-inspect"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectContainer(c);
                        }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Table Footer */}
      <div className="table-footer">
        <span>
          Showing <strong>{filtered.length}</strong> of <strong>{containers.length}</strong> containers
        </span>
      </div>
    </div>
  );
}
