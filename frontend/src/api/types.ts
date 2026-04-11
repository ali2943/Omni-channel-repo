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
  sla_compliance_percentage?: number;
  average_handle_time_minutes?: number;
  volume_by_channel: Record<string, number>;
  volume_by_status: Record<string, number>;
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
// Smart AI types (LangChain / LangGraph-powered)
// ---------------------------------------------------------------------------

/** Response from GET /ai/suggest-reply-smart/{ticket_id} */
export interface SmartAISuggestion {
  ticket_id: number;
  suggestions: string[];
  /** Recommended tone: "formal" | "empathetic" | "technical" */
  tone?: string;
  /** "langchain" when LLM was used, "keyword_fallback" otherwise */
  powered_by: string;
}

/** Response from POST /ai/classify-smart/{ticket_id} */
export interface SmartClassification {
  ticket_id: number;
  suggested_priority: string;
  suggested_category: string;
  reasoning?: string;
  suggested_department?: string;
  /** "langchain" when LLM was used, "keyword_fallback" otherwise */
  powered_by: string;
}

/** Response from POST /ai/process-with-workflow/{ticket_id} */
export interface WorkflowResult {
  ticket_id: number;
  priority: string;
  category: string;
  department: string;
  requires_human_review: boolean;
  auto_respond: boolean;
  suggested_response: string;
  routing_reason: string;
  workflow_steps: string[];
  /** "langgraph" when workflow ran, "keyword_fallback" otherwise */
  powered_by: string;
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

