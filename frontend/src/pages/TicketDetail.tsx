import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  getTicket,
  getMessages,
  listAgents,
  assignTicket,
  updateTicketStatus,
  addTag,
  removeTag,
  sendMessage,
  suggestReply,
  classifyTicket,
} from '../api';
import type { Ticket, Agent, Message, Tag } from '../api';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';

/**
 * Returns the WebSocket base URL.
 * In development the Vite proxy forwards /ws/* to the backend.
 * In production set VITE_WS_URL to the backend WebSocket URL (e.g. wss://api.example.com).
 */
function getWsBaseUrl(): string {
  if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}`;
}

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const ticketId = id ? Number(id) : null;
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedAgent, setSelectedAgent] = useState<number | ''>('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [newTag, setNewTag] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [senderType, setSenderType] = useState<'agent' | 'customer'>('agent');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!ticketId) return;

    const fetchAll = async () => {
      try {
        const [ticketData, agentList, msgList] = await Promise.all([
          getTicket(ticketId),
          listAgents(),
          getMessages(ticketId),
        ]);
        setTicket(ticketData);
        setAgents(agentList);
        setMessages(msgList);
        setSelectedStatus(ticketData.status);
      } catch {
        setError('Failed to load ticket data.');
      } finally {
        setLoading(false);
      }
    };

    fetchAll();

    // WebSocket connection — goes through Vite proxy in dev, or uses VITE_WS_URL in prod.
    const ws = new WebSocket(`${getWsBaseUrl()}/ws/tickets/${ticketId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          setMessages((prev) => [...prev, data.message]);
        } else if (data.type === 'ticket_update') {
          setTicket((prev) => (prev ? { ...prev, ...data.ticket } : prev));
        }
      } catch {
        // ignore parse errors
      }
    };

    return () => {
      ws.close();
    };
  }, [id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const showAction = (msg: string) => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(null), 3000);
  };

  const handleAssign = async () => {
    if (!ticketId || selectedAgent === '') return;
    try {
      const updated = await assignTicket(ticketId, selectedAgent);
      setTicket(updated);
      showAction('Agent assigned successfully.');
    } catch {
      showAction('Failed to assign agent.');
    }
  };

  const handleStatusUpdate = async () => {
    if (!ticketId || !selectedStatus) return;
    try {
      const updated = await updateTicketStatus(ticketId, selectedStatus);
      setTicket(updated);
      showAction('Status updated.');
    } catch {
      showAction('Failed to update status.');
    }
  };

  const handleAddTag = async () => {
    if (!ticketId || !newTag.trim()) return;
    try {
      const updated = await addTag(ticketId, newTag.trim());
      setTicket(updated);
      setNewTag('');
    } catch {
      showAction('Failed to add tag.');
    }
  };

  const handleRemoveTag = async (tag: Tag) => {
    if (!ticketId) return;
    try {
      const updated = await removeTag(ticketId, tag.id);
      setTicket(updated);
    } catch {
      showAction('Failed to remove tag.');
    }
  };

  const handleSendMessage = async () => {
    if (!ticketId || !messageInput.trim()) return;
    try {
      const msg = await sendMessage(ticketId, messageInput.trim(), senderType);
      setMessages((prev) => [...prev, msg]);
      setMessageInput('');
    } catch {
      showAction('Failed to send message.');
    }
  };

  const handleSuggestReply = async () => {
    if (!ticketId) return;
    try {
      const result = await suggestReply(ticketId);
      setSuggestions(result.suggestions);
    } catch {
      showAction('Failed to get AI suggestions.');
    }
  };

  const handleClassify = async () => {
    if (!ticketId) return;
    try {
      const result = await classifyTicket(ticketId);
      showAction(`Classified: priority=${result.priority}, category=${result.category}`);
      const updated = await getTicket(ticketId);
      setTicket(updated);
    } catch {
      showAction('Failed to classify ticket.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !ticket) {
    return <p className="text-red-500">{error ?? 'Ticket not found.'}</p>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{ticket.subject}</h2>
            <p className="text-sm text-gray-500 mt-1">
              Customer: <span className="font-medium">{ticket.customer_id}</span>
              {ticket.assigned_agent_id && (
                <>
                  {' '}· Agent:{' '}
                  <span className="font-medium">{ticket.assigned_agent_id}</span>
                </>
              )}
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <StatusBadge status={ticket.status} />
            <PriorityBadge priority={ticket.priority} />
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 capitalize">
              {ticket.channel}
            </span>
          </div>
        </div>

        {/* Tags */}
        <div className="mt-4 flex flex-wrap gap-2 items-center">
          {ticket.tags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-purple-100 text-purple-700"
            >
              {tag.name}
              <button
                onClick={() => handleRemoveTag(tag)}
                className="hover:text-red-600 font-bold"
              >
                ×
              </button>
            </span>
          ))}
          <div className="flex gap-1">
            <input
              type="text"
              placeholder="Add tag…"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
              className="border border-gray-300 rounded px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              onClick={handleAddTag}
              className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-0.5 rounded"
            >
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Action feedback */}
      {actionMessage && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg px-4 py-2 text-sm">
          {actionMessage}
        </div>
      )}

      {/* Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Assign Agent */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Assign Agent
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value === '' ? '' : Number(e.target.value))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select agent…</option>
            {agents.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleAssign}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg px-3 py-2"
          >
            Assign
          </button>
        </div>

        {/* Update Status */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Update Status
          </label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="closed">Closed</option>
          </select>
          <button
            onClick={handleStatusUpdate}
            className="w-full bg-gray-700 hover:bg-gray-800 text-white text-sm rounded-lg px-3 py-2"
          >
            Update
          </button>
        </div>

        {/* AI Classify */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Auto-Classify
          </label>
          <p className="text-xs text-gray-400">Use AI to classify ticket priority and category.</p>
          <button
            onClick={handleClassify}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg px-3 py-2"
          >
            Classify
          </button>
        </div>

        {/* AI Suggestions */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            AI Reply Suggestions
          </label>
          <button
            onClick={handleSuggestReply}
            className="w-full bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg px-3 py-2"
          >
            Suggest Replies
          </button>
          {suggestions.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setMessageInput(s)}
                  className="text-xs bg-green-50 border border-green-200 text-green-700 hover:bg-green-100 rounded-full px-2 py-0.5 text-left"
                >
                  {s.length > 40 ? s.slice(0, 40) + '…' : s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Message Thread */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div className="px-5 py-3 border-b border-gray-100">
          <h3 className="font-semibold text-gray-800">Messages</h3>
        </div>
        <div className="flex-1 overflow-y-auto p-5 space-y-3 max-h-96">
          {messages.length === 0 && (
            <p className="text-gray-400 text-sm text-center py-8">No messages yet.</p>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender_type === 'agent' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm ${
                  msg.sender_type === 'agent'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p>{msg.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    msg.sender_type === 'agent' ? 'text-blue-200' : 'text-gray-400'
                  }`}
                >
                  {msg.sender_type} · {new Date(msg.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-100 p-4 space-y-2">
          <div className="flex gap-2">
            <button
              onClick={() => setSenderType('agent')}
              className={`text-xs px-3 py-1 rounded-full border ${
                senderType === 'agent'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              Agent
            </button>
            <button
              onClick={() => setSenderType('customer')}
              className={`text-xs px-3 py-1 rounded-full border ${
                senderType === 'customer'
                  ? 'bg-gray-700 text-white border-gray-700'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              Customer
            </button>
          </div>
          <div className="flex gap-2">
            <textarea
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder="Type a message…"
              rows={2}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <button
              onClick={handleSendMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 rounded-lg text-sm font-medium"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
