import client from './client';
import type { AISuggestion, SmartAISuggestion, SmartClassification, Ticket, WorkflowResult } from './types';

export const suggestReply = async (ticket_id: number): Promise<AISuggestion> => {
  const { data } = await client.get(`/ai/suggest-reply/${ticket_id}`);
  return data;
};

export const classifyTicket = async (ticket_id: number): Promise<Ticket> => {
  const { data } = await client.post(`/ai/classify/${ticket_id}`);
  return data;
};

// ---------------------------------------------------------------------------
// Smart AI endpoints (LangChain / LangGraph-powered)
// ---------------------------------------------------------------------------

/**
 * Get LangChain-powered reply suggestions for a ticket.
 * Falls back to keyword-based suggestions when LLM is unavailable.
 * Check `powered_by` field in the response to see which path was used.
 */
export const suggestReplySmart = async (ticket_id: number): Promise<SmartAISuggestion> => {
  const { data } = await client.get(`/ai/suggest-reply-smart/${ticket_id}`);
  return data;
};

/**
 * Classify a ticket using LLM-based analysis (priority, category, department).
 * Falls back to keyword-based classification when LLM is unavailable.
 */
export const classifyTicketSmart = async (ticket_id: number): Promise<SmartClassification> => {
  const { data } = await client.post(`/ai/classify-smart/${ticket_id}`);
  return data;
};

/**
 * Process a ticket through the full LangGraph multi-step workflow.
 * Runs: classify → decide_response → route_agent → human_review nodes.
 * Falls back to simple keyword processing when LangGraph is unavailable.
 */
export const processWithWorkflow = async (ticket_id: number): Promise<WorkflowResult> => {
  const { data } = await client.post(`/ai/process-with-workflow/${ticket_id}`);
  return data;
};

