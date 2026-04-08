import { useEffect, useState } from 'react';
import { getQueue, autoAssign } from '../api';
import type { Ticket } from '../api';
import PriorityBadge from '../components/PriorityBadge';

const channelEmoji: Record<string, string> = {
  email: '📧',
  whatsapp: '💬',
  social: '📱',
  voice: '📞',
  shopify: '🛒',
  webchat: '🌐',
};

export default function RoutingQueue() {
  const [queue, setQueue] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<number, { msg: string; ok: boolean }>>({});

  const fetchQueue = async () => {
    try {
      const data = await getQueue();
      setQueue(data);
    } catch {
      setError('Failed to load routing queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleAutoAssign = async (ticketId: number) => {
    try {
      const result = await autoAssign(ticketId);
      setFeedback((prev) => ({
        ...prev,
        [ticketId]: {
          msg: result.assigned_agent_id
            ? `Assigned to agent #${result.assigned_agent_id}`
            : 'Assigned successfully.',
          ok: true,
        },
      }));
      await fetchQueue();
    } catch {
      setFeedback((prev) => ({
        ...prev,
        [ticketId]: { msg: 'Auto-assign failed.', ok: false },
      }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Routing Queue</h2>
        <button
          onClick={fetchQueue}
          className="text-sm text-gray-500 hover:text-gray-800 border border-gray-300 px-3 py-1.5 rounded-lg"
        >
          ↻ Refresh
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="text-left text-gray-600">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Subject</th>
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Channel</th>
              <th className="px-4 py-3 font-medium">Created At</th>
              <th className="px-4 py-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {queue.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                  No unassigned tickets in queue.
                </td>
              </tr>
            )}
            {queue.map((ticket) => (
              <tr key={ticket.id} className="border-t border-gray-100">
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                  #{ticket.id}
                </td>
                <td className="px-4 py-3 font-medium text-gray-900">{ticket.subject}</td>
                <td className="px-4 py-3">
                  <PriorityBadge priority={ticket.priority} />
                </td>
                <td className="px-4 py-3">
                  <span className="mr-1">{channelEmoji[ticket.channel ?? ''] ?? '📌'}</span>
                  <span className="capitalize">{ticket.channel}</span>
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {new Date(ticket.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleAutoAssign(ticket.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg"
                    >
                      Auto-Assign
                    </button>
                    {feedback[ticket.id] && (
                      <span
                        className={`text-xs ${
                          feedback[ticket.id].ok ? 'text-green-600' : 'text-red-500'
                        }`}
                      >
                        {feedback[ticket.id].msg}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
