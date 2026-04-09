import client from './client';
import type {
  Agent,
  KnowledgeDocument,
  AIAgentResponse,
  AgentAuditRecord,
} from './types';

// ---------------------------------------------------------------------------
// Create AI agent
// ---------------------------------------------------------------------------

export const createAIAgent = async (payload: {
  name: string;
  email: string;
  department?: string;
  skills?: string[];
  ai_model?: string;
  ai_config?: {
    temperature?: number;
    max_tokens?: number;
    system_prompt?: string;
  };
  knowledge_base_enabled?: boolean;
  auto_respond?: boolean;
  confidence_threshold?: number;
}): Promise<Agent> => {
  const { data } = await client.post('/ai-agents/', payload);
  return data;
};

// ---------------------------------------------------------------------------
// Knowledge base
// ---------------------------------------------------------------------------

export const addKnowledgeDocument = async (
  agentId: number,
  payload: { title: string; content: string; category?: string },
): Promise<KnowledgeDocument> => {
  const { data } = await client.post(`/ai-agents/${agentId}/knowledge`, payload);
  return data;
};

export const listKnowledgeDocuments = async (
  agentId: number,
): Promise<KnowledgeDocument[]> => {
  const { data } = await client.get(`/ai-agents/${agentId}/knowledge`);
  return data;
};

// ---------------------------------------------------------------------------
// Query
// ---------------------------------------------------------------------------

export const queryAIAgent = async (
  agentId: number,
  payload: { query: string; ticket_id?: number; use_knowledge_base?: boolean },
): Promise<AIAgentResponse> => {
  const { data } = await client.post(`/ai-agents/${agentId}/query`, payload);
  return data;
};

// ---------------------------------------------------------------------------
// Audit trail
// ---------------------------------------------------------------------------

export const listAIResponses = async (agentId: number): Promise<AgentAuditRecord[]> => {
  const { data } = await client.get(`/ai-agents/${agentId}/responses`);
  return data;
};
