import client from './client';
import type { AISuggestion, ClassifyResult } from './types';

export const suggestReply = async (ticket_id: number): Promise<AISuggestion> => {
  const { data } = await client.get(`/ai/suggest-reply/${ticket_id}`);
  return data;
};

export const classifyTicket = async (ticket_id: number): Promise<ClassifyResult> => {
  const { data } = await client.post(`/ai/classify/${ticket_id}`);
  return data;
};
