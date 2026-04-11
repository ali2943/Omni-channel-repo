import axios from 'axios';

// In development the Vite dev-server proxy rewrites /api/* → backend.
// In production set VITE_API_URL to the full backend base URL (e.g. https://api.example.com).
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
});

// Log outgoing requests in development to aid debugging.
client.interceptors.request.use((config) => {
  console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data ?? '');
  return config;
});

// Normalise error messages so callers always receive an Error with a readable message.
client.interceptors.response.use(
  (response) => {
    console.debug(`[API] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    const detail = error.response?.data?.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : error.message ?? 'An unexpected error occurred.';
    console.error(
      `[API] Error ${error.response?.status ?? 'network'} ${error.config?.url}:`,
      message,
      error,
    );
    return Promise.reject(new Error(message));
  }
);

export default client;
