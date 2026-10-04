import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import MetricCards from './components/MetricCards';
import ContainerTable from './components/ContainerTable';
import ContainerDetails from './components/ContainerDetails';
import { getContainers, getBackendHealth } from './services/api';

// DevOps Demo Mock Containers (matching Member 1 & Member 2 specification)
export const SAMPLE_CONTAINERS = [
  {
    id: "c1a89b42e71d",
    name: "web-frontend",
    status: "running",
    cpu: 35.5,
    memory: 45.0,
    restarts: 0,
    health: "HEALTHY",
    reasons: []
  },
  {
    id: "e2f034d8129a",
    name: "api-gateway",
    status: "running",
    cpu: 78.0,
    memory: 65.0,
    restarts: 1,
    health: "WARNING",
    reasons: ["High CPU usage", "Container restarts detected"]
  },
  {
    id: "9b12cc8541fe",
    name: "database-cluster",
    status: "running",
    cpu: 92.0,
    memory: 87.0,
    restarts: 3,
    health: "CRITICAL",
    reasons: [
      "High CPU usage",
      "High memory usage",
      "Multiple container restarts"
    ]
  },
  {
    id: "4d55aa6190ec",
    name: "payment-service",
    status: "stopped",
    cpu: 0.0,
    memory: 0.0,
    restarts: 0,
    health: "FAILED",
    reasons: ["Container is not running (status: stopped)"]
  },
  {
    id: "781bb49301fa",
    name: "redis-cache",
    status: "running",
    cpu: 12.4,
    memory: 22.8,
    restarts: 0,
    health: "HEALTHY",
    reasons: []
  }
];

export default function App() {
  const [containers, setContainers] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking' | 'online' | 'docker_unavailable' | 'offline'
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [healthFilter, setHealthFilter] = useState('ALL');
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const isMounted = useRef(true);
  const isFetchingRef = useRef(false);

  // Fetch container metrics and health status from FastAPI
  const loadData = useCallback(async (isManual = false) => {
    if (isDemoMode) {
      if (isManual) setIsRefreshing(true);
      setTimeout(() => {
        if (!isMounted.current) return;
        setContainers(SAMPLE_CONTAINERS);
        setLastUpdated(new Date());
        setIsRefreshing(false);
      }, 300);
      return;
    }

    if (isFetchingRef.current && !isManual) {
      return; // Avoid overlapping automatic polls while Docker stats are being calculated
    }

    isFetchingRef.current = true;
    if (isManual) {
      setIsRefreshing(true);
    }

    try {
      // Directly query live containers from backend
      const containerData = await getContainers();
      if (!isMounted.current) return;

      setContainers(Array.isArray(containerData) ? containerData : []);
      setBackendStatus('online');
      setErrorMessage('');
      setLastUpdated(new Date());

      // If a container is currently open in modal, update its data
      setSelectedContainer((current) => {
        if (!current) return null;
        return containerData.find((c) => c.id === current.id) || current;
      });
    } catch (err) {
      if (!isMounted.current) return;

      if (err.status === 503) {
        setBackendStatus('docker_unavailable');
        setErrorMessage(
          err.message || 'Docker daemon is unreachable. Please verify Docker Desktop is running.'
        );
      } else {
        // Test if FastAPI itself is responding or completely offline
        try {
          await getBackendHealth();
          setBackendStatus('online');
          setErrorMessage(err.message || 'Error collecting container metrics from Docker.');
        } catch {
          setBackendStatus('offline');
          setErrorMessage(
            'FastAPI backend server is unreachable. Ensure the backend is running at http://127.0.0.1:8000'
          );
        }
      }
    } finally {
      isFetchingRef.current = false;
      if (isMounted.current) {
        setIsRefreshing(false);
      }
    }
  }, [isDemoMode]);

  // Initial load
  useEffect(() => {
    isMounted.current = true;
    loadData();

    return () => {
      isMounted.current = false;
    };
  }, [loadData]);

  // Auto-refresh interval (every 10 seconds, matching prompt requirements)
  useEffect(() => {
    if (!autoRefresh || isDemoMode) return;

    const intervalId = setInterval(() => {
      loadData(false);
    }, 10000);

    return () => clearInterval(intervalId);
  }, [autoRefresh, isDemoMode, loadData]);

  const enableDemoMode = () => {
    setIsDemoMode(true);
    setContainers(SAMPLE_CONTAINERS);
    setErrorMessage('');
    setLastUpdated(new Date());
  };

  const disableDemoMode = () => {
    setIsDemoMode(false);
    setContainers([]);
    loadData(true);
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <Header
        backendStatus={isDemoMode ? 'demo' : backendStatus}
        isRefreshing={isRefreshing}
        onRefresh={() => loadData(true)}
        autoRefresh={autoRefresh && !isDemoMode}
        onToggleAutoRefresh={setAutoRefresh}
        lastUpdated={lastUpdated}
        isDemoMode={isDemoMode}
        onToggleDemo={isDemoMode ? disableDemoMode : enableDemoMode}
      />

      <main className="dashboard-content">
        {/* Demo Mode Announcement */}
        {isDemoMode && (
          <div className="demo-banner">
            <span className="demo-badge">Demo Mode Active</span>
            <span className="demo-text">
              Displaying standard ContainerCare test containers (Healthy, Warning, Critical, Failed) from Member 1 & 2 specs.
            </span>
            <button type="button" className="btn-demo-switch" onClick={disableDemoMode}>
              Switch to Live Docker API
            </button>
          </div>
        )}

        {/* Connection or Daemon Alert Banner */}
        {!isDemoMode && errorMessage && (
          <div className={`alert-banner ${backendStatus === 'docker_unavailable' ? 'banner-warning' : 'banner-error'}`}>
            <div className="banner-icon-box">
              <svg className="banner-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="banner-message-wrap">
              <h4 className="banner-title">
                {backendStatus === 'docker_unavailable'
                  ? 'Docker Desktop Daemon Offline'
                  : 'Backend Connection Failed'}
              </h4>
              <p className="banner-desc">{errorMessage}</p>
            </div>
            <div className="banner-actions">
              <button
                type="button"
                className="btn-retry"
                onClick={() => loadData(true)}
                disabled={isRefreshing}
              >
                {isRefreshing ? 'Retrying...' : 'Retry Connection'}
              </button>
              <button
                type="button"
                className="btn-demo"
                onClick={enableDemoMode}
              >
                View Sample Containers
              </button>
            </div>
          </div>
        )}

        {/* KPI / Metric Summary Cards */}
        <MetricCards
          containers={containers}
          activeFilter={healthFilter}
          onSelectFilter={(filterId) => setHealthFilter(filterId)}
        />

        {/* Main Monitoring Inventory Table */}
        <ContainerTable
          containers={containers}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          healthFilter={healthFilter}
          onFilterChange={setHealthFilter}
          onSelectContainer={setSelectedContainer}
        />
      </main>

      {/* Container Inspection Modal */}
      {selectedContainer && (
        <ContainerDetails
          container={selectedContainer}
          onClose={() => setSelectedContainer(null)}
        />
      )}
    </div>
  );
}
