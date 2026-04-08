import client from './client';
import type { Ticket, Message, Tag } from './types';

export const listTickets = async (): Promise<Ticket[]> => {
  const { data } = await client.get('/tickets/');
  return data;
};

export const getTicket = async (id: number): Promise<Ticket> => {
  const { data } = await client.get(`/tickets/${id}`);
  return data;
};

export const createTicket = async (payload: {
  customer_id: number;
  channel?: string;
  subject?: string;
  priority?: string;
}): Promise<Ticket> => {
  const { data } = await client.post('/tickets/', payload);
  return data;
};

export const assignTicket = async (id: number, agent_id: number): Promise<Ticket> => {
  const { data } = await client.put(`/tickets/${id}/assign`, { agent_id });
  return data;
};

export const updateTicketStatus = async (id: number, status: string): Promise<Ticket> => {
  const { data } = await client.put(`/tickets/${id}/status`, { status });
  return data;
};

export const addTag = async (id: number, tag: string): Promise<Ticket> => {
  const { data } = await client.post(`/tickets/${id}/tags`, { name: tag });
  return data;
};

export const removeTag = async (ticketId: number, tagId: number): Promise<Ticket> => {
  // Both IDs are server-issued integers; validate before embedding in the URL path.
  if (!Number.isInteger(ticketId) || !Number.isInteger(tagId)) {
    throw new Error('Invalid ticket or tag identifier.');
  }
  const { data } = await client.delete(`/tickets/${ticketId}/tags/${tagId}`);
  return data;
};

export const sendMessage = async (
  ticket_id: number,
  content: string,
  sender_type: 'agent' | 'customer'
): Promise<Message> => {
  const { data } = await client.post(`/tickets/${ticket_id}/messages`, {
    content,
    sender_type,
  });
  return data;
};

export const getMessages = async (ticket_id: number): Promise<Message[]> => {
  const { data } = await client.get(`/tickets/${ticket_id}/messages`);
  return data;
};

export const listTags = async (): Promise<Tag[]> => {
  const { data } = await client.get('/tags/');
  return data;
};
