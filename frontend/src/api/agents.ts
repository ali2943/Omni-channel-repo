import client from './client';
import type { Agent } from './types';

export const listAgents = async (): Promise<Agent[]> => {
  const { data } = await client.get('/agents/');
  return data;
};

export const getAgent = async (id: number): Promise<Agent> => {
  const { data } = await client.get(`/agents/${id}`);
  return data;
};

export const createAgent = async (payload: {
  name: string;
  email: string;
  department: string;
  skills: string[];
}): Promise<Agent> => {
  const { data } = await client.post('/agents/', payload);
  return data;
};

// Note: the backend's /agents/login endpoint only requires an email address
// (no password) as the User schema does not store credentials.
export const loginAgent = async (email: string): Promise<Agent> => {
  const { data } = await client.post('/agents/login', { email });
  return data;
};

export const updateSkills = async (id: number, skills: string[]): Promise<Agent> => {
  const { data } = await client.put(`/agents/${id}/skills`, { skills });
  return data;
};

export const updateAvailability = async (id: number, is_available: boolean): Promise<Agent> => {
  const { data } = await client.put(`/agents/${id}/availability`, { is_available });
  return data;
};
