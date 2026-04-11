import client from './client';
import type { KPI, SLA, VolumeEntry } from './types';

export const getKPIs = async (): Promise<KPI> => {
  const { data } = await client.get('/analytics/kpis');
  return data;
};

export const getSLA = async (): Promise<SLA> => {
  const { data } = await client.get('/analytics/sla');
  return data;
};

export const getVolume = async (): Promise<VolumeEntry[]> => {
  const { data } = await client.get('/analytics/volume');
  if (!Array.isArray(data)) {
    console.warn('getVolume: unexpected response format, expected array but got', typeof data);
    return [];
  }
  return data;
};
