import client from './client';

// ---- Types ----

export interface Ticket {
  id: string;
  subject: string;
  status: 'open' | 'in_progress' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  channel: string;
  customer_id: string;
  assigned_agent_id: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  name: string;
  email: string;
  department: string;
  skills: string[];
  is_available: boolean;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  created_at: string;
}

export interface Message {
  id: string;
  ticket_id: string;
  sender_type: 'agent' | 'customer';
  content: string;
  created_at: string;
}

export interface KPI {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  closed_tickets: number;
  sla_compliance_percentage: number;
  average_handle_time_minutes: number;
}

export interface SLA {
  compliant: number;
  breached: number;
  compliance_rate: number;
}

export interface VolumeEntry {
  channel: string;
  count: number;
}

export interface Tag {
  id: string;
  name: string;
}

export interface QueueTicket {
  id: string;
  subject: string;
  priority: string;
  channel: string;
  created_at: string;
}

export interface AISuggestion {
  suggestions: string[];
}

export interface ClassifyResult {
  priority: string;
  category: string;
}

// ---- Analytics ----

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
  return data;
};

// ---- Tickets ----

export const listTickets = async (): Promise<Ticket[]> => {
  const { data } = await client.get('/tickets/');
  return data;
};

export const getTicket = async (id: string): Promise<Ticket> => {
  const { data } = await client.get(`/tickets/${id}`);
  return data;
};

export const createTicket = async (payload: Partial<Ticket>): Promise<Ticket> => {
  const { data } = await client.post('/tickets/', payload);
  return data;
};

export const assignTicket = async (id: string, agent_id: string): Promise<Ticket> => {
  const { data } = await client.put(`/tickets/${id}/assign`, { agent_id });
  return data;
};

export const updateTicketStatus = async (id: string, status: string): Promise<Ticket> => {
  const { data } = await client.put(`/tickets/${id}/status`, { status });
  return data;
};

export const addTag = async (id: string, tag: string): Promise<Ticket> => {
  const { data } = await client.post(`/tickets/${id}/tags`, { tag });
  return data;
};

export const removeTag = async (id: string, tag: string): Promise<Ticket> => {
  const { data } = await client.delete(`/tickets/${id}/tags/${encodeURIComponent(tag)}`);
  return data;
};

export const sendMessage = async (
  ticket_id: string,
  content: string,
  sender_type: 'agent' | 'customer'
): Promise<Message> => {
  const { data } = await client.post(`/tickets/${ticket_id}/messages`, {
    content,
    sender_type,
  });
  return data;
};

export const getMessages = async (ticket_id: string): Promise<Message[]> => {
  const { data } = await client.get(`/tickets/${ticket_id}/messages`);
  return data;
};

// ---- Agents ----

export const listAgents = async (): Promise<Agent[]> => {
  const { data } = await client.get('/agents/');
  return data;
};

export const getAgent = async (id: string): Promise<Agent> => {
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

export const loginAgent = async (email: string, password: string): Promise<Agent> => {
  const { data } = await client.post('/agents/login', { email, password });
  return data;
};

export const updateSkills = async (id: string, skills: string[]): Promise<Agent> => {
  const { data } = await client.put(`/agents/${id}/skills`, { skills });
  return data;
};

export const updateAvailability = async (id: string, is_available: boolean): Promise<Agent> => {
  const { data } = await client.put(`/agents/${id}/availability`, { is_available });
  return data;
};

// ---- Customers ----

export const getCustomer = async (id: string): Promise<Customer> => {
  const { data } = await client.get(`/customers/${id}`);
  return data;
};

export const createCustomer = async (payload: {
  name: string;
  email: string;
  phone?: string;
}): Promise<Customer> => {
  const { data } = await client.post('/customers/', payload);
  return data;
};

// ---- Routing ----

export const getQueue = async (): Promise<QueueTicket[]> => {
  const { data } = await client.get('/routing/queue');
  return data;
};

export const autoAssign = async (ticket_id: string): Promise<{ message: string; agent_id: string }> => {
  const { data } = await client.post(`/routing/auto-assign/${ticket_id}`);
  return data;
};

// ---- AI ----

export const suggestReply = async (ticket_id: string): Promise<AISuggestion> => {
  const { data } = await client.get(`/ai/suggest-reply/${ticket_id}`);
  return data;
};

export const classifyTicket = async (ticket_id: string): Promise<ClassifyResult> => {
  const { data } = await client.post(`/ai/classify/${ticket_id}`);
  return data;
};

// ---- Tags ----

export const listTags = async (): Promise<Tag[]> => {
  const { data } = await client.get('/tags/');
  return data;
};

// ---- Simulate ----

export const simulateEmail = async (payload: {
  customer_name: string;
  customer_email: string;
  subject: string;
  body: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/email', payload);
  return data;
};

export const simulateWhatsApp = async (payload: {
  customer_name: string;
  customer_phone: string;
  message: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/whatsapp', payload);
  return data;
};

export const simulateSocial = async (payload: {
  platform: string;
  customer_handle: string;
  message: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/social', payload);
  return data;
};

export const simulateVoice = async (payload: {
  customer_name: string;
  customer_phone: string;
  notes: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/voice', payload);
  return data;
};

export const simulateShopify = async (payload: {
  customer_name: string;
  customer_email: string;
  order_id: string;
  issue: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/shopify', payload);
  return data;
};

export const simulateWebchat = async (payload: {
  customer_name: string;
  customer_email: string;
  message: string;
}): Promise<{ ticket_id: string }> => {
  const { data } = await client.post('/simulate/webchat', payload);
  return data;
};
