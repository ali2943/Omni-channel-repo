import axios from 'axios';

// In development the Vite dev-server proxy rewrites /api/* → backend.
// In production set VITE_API_URL to the full backend base URL (e.g. https://api.example.com).
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
});

// Normalise error messages so callers always receive an Error with a readable message.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : error.message ?? 'An unexpected error occurred.';
    return Promise.reject(new Error(message));
  }
);

export default client;
