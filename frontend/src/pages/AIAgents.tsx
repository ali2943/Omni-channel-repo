import { useEffect, useState } from 'react';
import {
  createAIAgent,
  listAgents,
  addKnowledgeDocument,
  listKnowledgeDocuments,
  queryAIAgent,
  listAIResponses,
} from '../api';
import type { Agent, KnowledgeDocument, AIAgentResponse, AgentAuditRecord } from '../api';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CreateAIAgentForm {
  name: string;
  email: string;
  department: string;
  ai_model: string;
  system_prompt: string;
  temperature: string;
  max_tokens: string;
  auto_respond: boolean;
  confidence_threshold: string;
}

const defaultCreateForm: CreateAIAgentForm = {
  name: '',
  email: '',
  department: 'support',
  ai_model: 'gpt-3.5-turbo',
  system_prompt: 'You are a helpful support agent.',
  temperature: '0.7',
  max_tokens: '500',
  auto_respond: false,
  confidence_threshold: '0.7',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AIAgents() {
  const [aiAgents, setAIAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create agent modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState<CreateAIAgentForm>(defaultCreateForm);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Selected agent panels
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [activeTab, setActiveTab] = useState<'knowledge' | 'query' | 'audit'>('knowledge');

  // Knowledge base
  const [knowledgeDocs, setKnowledgeDocs] = useState<KnowledgeDocument[]>([]);
  const [kbForm, setKbForm] = useState({ title: '', content: '', category: 'General' });
  const [addingKb, setAddingKb] = useState(false);
  const [kbError, setKbError] = useState<string | null>(null);
  const [kbSuccess, setKbSuccess] = useState(false);

  // Query
  const [queryText, setQueryText] = useState('');
  const [querying, setQuerying] = useState(false);
  const [queryResult, setQueryResult] = useState<AIAgentResponse | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  // Audit trail
  const [auditRecords, setAuditRecords] = useState<AgentAuditRecord[]>([]);

  // ---------------------------------------------------------------------------
  // Fetch AI agents (filter from all agents)
  // ---------------------------------------------------------------------------
  const fetchAIAgents = async () => {
    try {
      const all = await listAgents();
      setAIAgents(all.filter((a) => a.is_ai_agent));
    } catch {
      setError('Failed to load AI agents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAIAgents();
  }, []);

  // ---------------------------------------------------------------------------
  // Create AI agent
  // ---------------------------------------------------------------------------
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);
    try {
      await createAIAgent({
        name: createForm.name,
        email: createForm.email,
        department: createForm.department,
        ai_model: createForm.ai_model,
        ai_config: {
          temperature: parseFloat(createForm.temperature),
          max_tokens: parseInt(createForm.max_tokens, 10),
          system_prompt: createForm.system_prompt,
        },
        auto_respond: createForm.auto_respond,
        confidence_threshold: parseFloat(createForm.confidence_threshold),
        knowledge_base_enabled: true,
      });
      setShowCreateModal(false);
      setCreateForm(defaultCreateForm);
      await fetchAIAgents();
    } catch {
      setCreateError('Failed to create AI agent. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Select agent → load knowledge & audit
  // ---------------------------------------------------------------------------
  const selectAgent = async (agent: Agent) => {
    setSelectedAgent(agent);
    setActiveTab('knowledge');
    setQueryResult(null);
    setQueryText('');
    setKbSuccess(false);
    await Promise.all([loadKnowledge(agent.id), loadAudit(agent.id)]);
  };

  const loadKnowledge = async (agentId: number) => {
    try {
      const docs = await listKnowledgeDocuments(agentId);
      setKnowledgeDocs(docs);
    } catch {
      /* ignore */
    }
  };

  const loadAudit = async (agentId: number) => {
    try {
      const records = await listAIResponses(agentId);
      setAuditRecords(records);
    } catch {
      /* ignore */
    }
  };

  // ---------------------------------------------------------------------------
  // Add knowledge document
  // ---------------------------------------------------------------------------
  const handleAddKnowledge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent) return;
    setAddingKb(true);
    setKbError(null);
    setKbSuccess(false);
    try {
      await addKnowledgeDocument(selectedAgent.id, kbForm);
      setKbForm({ title: '', content: '', category: 'General' });
      setKbSuccess(true);
      await loadKnowledge(selectedAgent.id);
    } catch {
      setKbError('Failed to add knowledge document.');
    } finally {
      setAddingKb(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Query agent
  // ---------------------------------------------------------------------------
  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !queryText.trim()) return;
    setQuerying(true);
    setQueryError(null);
    setQueryResult(null);
    try {
      const result = await queryAIAgent(selectedAgent.id, {
        query: queryText,
        use_knowledge_base: true,
      });
      setQueryResult(result);
      await loadAudit(selectedAgent.id);
    } catch {
      setQueryError('Query failed. Check your OPENAI_API_KEY and try again.');
    } finally {
      setQuerying(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------
  const confidenceBadge = (score: number) => {
    const pct = Math.round(score * 100);
    const color =
      pct >= 70 ? 'bg-green-100 text-green-700' :
      pct >= 40 ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700';
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
        {pct}% confidence
      </span>
    );
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600" />
      </div>
    );
  }

  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="flex gap-6 h-full">
      {/* ---- Left panel: agent list ---- */}
      <div className="w-72 flex-shrink-0 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">🤖 AI Agents</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg"
          >
            + New
          </button>
        </div>

        {aiAgents.length === 0 ? (
          <p className="text-gray-500 text-sm">No AI agents yet. Create one to get started.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {aiAgents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => selectAgent(agent)}
                className={`text-left rounded-xl border p-4 transition-colors ${
                  selectedAgent?.id === agent.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-100 bg-white hover:border-purple-300'
                }`}
              >
                <p className="font-semibold text-gray-900 text-sm">{agent.name}</p>
                <p className="text-xs text-gray-500">{agent.email}</p>
                <p className="text-xs text-gray-400 mt-1">
                  Model: <span className="font-mono">{agent.ai_model ?? '—'}</span>
                </p>
                <div className="flex gap-2 mt-2">
                  {agent.auto_respond && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      Auto-respond
                    </span>
                  )}
                  {agent.knowledge_base_enabled && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                      KB enabled
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ---- Right panel: agent detail ---- */}
      {selectedAgent ? (
        <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="border-b border-gray-100 px-6 py-4">
            <h3 className="font-bold text-gray-900 text-lg">{selectedAgent.name}</h3>
            <p className="text-sm text-gray-500">{selectedAgent.email}</p>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-100 px-6 flex gap-4">
            {(['knowledge', 'query', 'audit'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-3 text-sm font-medium border-b-2 capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab === 'knowledge' ? '📚 Knowledge Base' :
                 tab === 'query'     ? '💬 Query Agent' :
                                       '📋 Audit Trail'}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-auto p-6">

            {/* --- Knowledge Base tab --- */}
            {activeTab === 'knowledge' && (
              <div className="space-y-6">
                {/* Add document form */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <h4 className="font-semibold text-gray-700 mb-3 text-sm">Add Knowledge Document</h4>
                  <form onSubmit={handleAddKnowledge} className="space-y-3">
                    {kbError && (
                      <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">{kbError}</p>
                    )}
                    {kbSuccess && (
                      <p className="text-sm text-green-600 bg-green-50 rounded px-3 py-2">
                        ✓ Document added successfully.
                      </p>
                    )}
                    <input
                      required
                      placeholder="Title"
                      value={kbForm.title}
                      onChange={(e) => setKbForm((f) => ({ ...f, title: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <input
                      placeholder="Category (e.g. FAQ, Policy)"
                      value={kbForm.category}
                      onChange={(e) => setKbForm((f) => ({ ...f, category: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <textarea
                      required
                      rows={4}
                      placeholder="Content…"
                      value={kbForm.content}
                      onChange={(e) => setKbForm((f) => ({ ...f, content: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                    />
                    <button
                      type="submit"
                      disabled={addingKb}
                      className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg"
                    >
                      {addingKb ? 'Adding…' : 'Add Document'}
                    </button>
                  </form>
                </div>

                {/* Document list */}
                {knowledgeDocs.length === 0 ? (
                  <p className="text-gray-400 text-sm">No documents yet.</p>
                ) : (
                  <div className="space-y-3">
                    {knowledgeDocs.map((doc) => (
                      <div
                        key={doc.id}
                        className="border border-gray-100 rounded-xl p-4 space-y-1"
                      >
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-gray-800 text-sm">{doc.title}</p>
                          {doc.category && (
                            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                              {doc.category}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 line-clamp-2">{doc.content}</p>
                        <p className="text-xs text-gray-400">
                          Added {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* --- Query tab --- */}
            {activeTab === 'query' && (
              <div className="space-y-6">
                <form onSubmit={handleQuery} className="space-y-3">
                  {queryError && (
                    <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2">{queryError}</p>
                  )}
                  <textarea
                    required
                    rows={3}
                    placeholder="Type a customer query…"
                    value={queryText}
                    onChange={(e) => setQueryText(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                  />
                  <button
                    type="submit"
                    disabled={querying}
                    className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg"
                  >
                    {querying ? 'Querying…' : 'Ask Agent'}
                  </button>
                </form>

                {queryResult && (
                  <div className="border border-purple-100 bg-purple-50 rounded-xl p-5 space-y-4">
                    <div className="flex items-start justify-between gap-3">
                      <h4 className="font-semibold text-purple-800 text-sm">Agent Response</h4>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {confidenceBadge(queryResult.confidence_score)}
                        {queryResult.requires_human_review && (
                          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">
                            ⚠ Human review
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm whitespace-pre-wrap">
                      {queryResult.response}
                    </p>
                    {queryResult.sources.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-2">Sources used:</p>
                        <div className="flex flex-wrap gap-2">
                          {queryResult.sources.map((src) => (
                            <span
                              key={src.id}
                              className="text-xs bg-white border border-purple-200 text-purple-700 px-2 py-0.5 rounded-full"
                            >
                              {src.title} ({Math.round(src.score * 100)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* --- Audit trail tab --- */}
            {activeTab === 'audit' && (
              <div className="space-y-3">
                {auditRecords.length === 0 ? (
                  <p className="text-gray-400 text-sm">No responses recorded yet.</p>
                ) : (
                  auditRecords.map((rec) => (
                    <div
                      key={rec.id}
                      className="border border-gray-100 rounded-xl p-4 space-y-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-xs text-gray-400">
                          Ticket #{rec.ticket_id} &middot; {new Date(rec.created_at).toLocaleString()}
                        </p>
                        <div className="flex items-center gap-2">
                          {rec.confidence_score != null &&
                            confidenceBadge(rec.confidence_score)}
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              rec.human_review_status === 'approved'
                                ? 'bg-green-100 text-green-700'
                                : rec.human_review_status === 'rejected'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}
                          >
                            {rec.human_review_status}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500">
                        <span className="font-medium">Q:</span> {rec.customer_query}
                      </p>
                      <p className="text-xs text-gray-700">
                        <span className="font-medium">A:</span> {rec.ai_response}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          <p className="text-sm">Select an AI agent to manage it</p>
        </div>
      )}

      {/* ---- Create AI agent modal ---- */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md mx-4 overflow-y-auto max-h-[90vh]">
            <h3 className="text-lg font-bold text-gray-900 mb-4">New AI Agent</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              {createError && (
                <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
                  {createError}
                </p>
              )}

              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  required
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  required
                  type="email"
                  value={createForm.email}
                  onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Department */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  value={createForm.department}
                  onChange={(e) => setCreateForm((f) => ({ ...f, department: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* LLM model */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">LLM Model</label>
                <select
                  value={createForm.ai_model}
                  onChange={(e) => setCreateForm((f) => ({ ...f, ai_model: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                  <option value="gpt-4">gpt-4</option>
                  <option value="gpt-4-turbo">gpt-4-turbo</option>
                  <option value="gpt-4o">gpt-4o</option>
                </select>
              </div>

              {/* System prompt */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
                <textarea
                  rows={3}
                  value={createForm.system_prompt}
                  onChange={(e) => setCreateForm((f) => ({ ...f, system_prompt: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                />
              </div>

              {/* Temperature / max tokens */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
                  <input
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    value={createForm.temperature}
                    onChange={(e) => setCreateForm((f) => ({ ...f, temperature: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max tokens</label>
                  <input
                    type="number"
                    min="50"
                    max="4096"
                    step="50"
                    value={createForm.max_tokens}
                    onChange={(e) => setCreateForm((f) => ({ ...f, max_tokens: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Confidence threshold */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confidence threshold{' '}
                  <span className="text-gray-400 font-normal">(0–1, below triggers human review)</span>
                </label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
                  value={createForm.confidence_threshold}
                  onChange={(e) =>
                    setCreateForm((f) => ({ ...f, confidence_threshold: e.target.value }))
                  }
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Auto-respond toggle */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="auto_respond"
                  checked={createForm.auto_respond}
                  onChange={(e) => setCreateForm((f) => ({ ...f, auto_respond: e.target.checked }))}
                  className="h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                />
                <label htmlFor="auto_respond" className="text-sm font-medium text-gray-700">
                  Enable auto-respond
                </label>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg"
                >
                  {creating ? 'Creating…' : 'Create AI Agent'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setCreateForm(defaultCreateForm);
                    setCreateError(null);
                  }}
                  className="flex-1 border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium py-2 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
