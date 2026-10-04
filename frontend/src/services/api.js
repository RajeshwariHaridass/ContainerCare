/**
 * api.js
 * Centralized API client for ContainerCare backend.
 * Base URL is configurable via VITE_API_URL environment variable.
 * Defaults to relative /api which is proxied by Nginx in Docker and by Vite in dev.
 */

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/$/, '');
  }
  return '';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Helper to perform fetch requests with timeout and structured error handling.
 */
async function apiRequest(endpoint, timeoutMs = 25000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });

    clearTimeout(timer);

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          errorMessage = typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Non-JSON error body
      }
      const error = new Error(errorMessage);
      error.status = response.status;
      throw error;
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      const abortError = new Error('Request timed out while contacting backend.');
      abortError.status = 408;
      throw abortError;
    }
    throw err;
  }
}

/**
 * Checks if the FastAPI backend service is reachable.
 * Calls GET /api/health
 */
export async function getBackendHealth() {
  return await apiRequest('/api/health', 8000);
}

/**
 * Retrieves the list of all containers with evaluated health and metrics.
 * Calls GET /api/containers
 */
export async function getContainers() {
  return await apiRequest('/api/containers', 30000);
}

export { API_BASE_URL };
