import client from './client';
import type { Ticket } from './types';

// Returns the list of open, unassigned tickets ordered by priority then age.
export const getQueue = async (): Promise<Ticket[]> => {
  const { data } = await client.get('/routing/queue');
  return data;
};

// Auto-assigns a ticket to the best available agent and returns the updated ticket.
export const autoAssign = async (ticket_id: number): Promise<Ticket> => {
  const { data } = await client.post(`/routing/auto-assign/${ticket_id}`);
  return data;
};
