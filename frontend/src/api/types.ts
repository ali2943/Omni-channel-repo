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
  is_ai_agent?: boolean;
  ai_model?: string | null;
  knowledge_base_enabled?: boolean;
  auto_respond?: boolean;
  confidence_threshold?: number;
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

// ---------------------------------------------------------------------------
// AI Agent types
// ---------------------------------------------------------------------------

export interface KnowledgeDocument {
  id: number;
  agent_id: number;
  title: string;
  content: string;
  category: string | null;
  embedding_model: string | null;
  created_at: string;
}

export interface AISource {
  id: number;
  title: string;
  category: string | null;
  score: number;
}

export interface AIAgentResponse {
  response: string;
  confidence_score: number;
  sources: AISource[];
  requires_human_review: boolean;
}

export interface AgentAuditRecord {
  id: number;
  agent_id: number;
  ticket_id: number;
  customer_query: string;
  ai_response: string;
  confidence_score: number | null;
  sources_used: string | null;
  human_review_status: string;
  created_at: string;
}

