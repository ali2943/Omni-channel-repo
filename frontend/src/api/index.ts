// Re-export all types
export type {
  Tag,
  Ticket,
  Agent,
  Customer,
  Message,
  KPI,
  SLA,
  VolumeEntry,
  AISuggestion,
  KnowledgeDocument,
  AIAgentResponse,
  AISource,
  AgentAuditRecord,
} from './types';

// Re-export domain API functions
export * from './tickets';
export * from './agents';
export * from './customers';
export * from './analytics';
export * from './ai';
export * from './routing';
export * from './simulate';
export * from './ai_agents';
