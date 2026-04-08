// Shared TypeScript types that mirror the backend Pydantic schemas.

export interface Tag {
  id: number;
  name: string;
}

export interface Ticket {
  id: number;
  subject: string | null;
  status: 'open' | 'in_progress' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  channel: string | null;
  customer_id: number;
  assigned_agent_id: number | null;
  category: string | null;
  tags: Tag[];
  created_at: string;
  sla_due_at: string | null;
  first_response_at: string | null;
  closed_at: string | null;
}

export interface Agent {
  id: number;
  name: string;
  email: string;
  department: string | null;
  skills: string[];
  is_available: boolean;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string;
  created_at: string;
}

export interface Message {
  id: number;
  ticket_id: number;
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

export interface AISuggestion {
  suggestions: string[];
}

export interface ClassifyResult {
  priority: string;
  category: string;
}
