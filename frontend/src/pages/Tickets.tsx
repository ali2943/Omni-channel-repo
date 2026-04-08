import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listTickets } from '../api';
import type { Ticket } from '../api';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';

const channelEmoji: Record<string, string> = {
  email: '📧',
  whatsapp: '💬',
  social: '📱',
  voice: '📞',
  shopify: '🛒',
  webchat: '🌐',
};

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const data = await listTickets();
        setTickets(data);
      } catch {
        setError('Failed to load tickets.');
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, []);

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
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Tickets</h2>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="text-left text-gray-600">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Subject</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Channel</th>
              <th className="px-4 py-3 font-medium">Created At</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                  No tickets found.
                </td>
              </tr>
            )}
            {tickets.map((ticket) => (
              <tr
                key={ticket.id}
                className="border-t border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/tickets/${ticket.id}`)}
              >
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                  #{ticket.id}
                </td>
                <td className="px-4 py-3 font-medium text-gray-900">{ticket.subject}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={ticket.status} />
                </td>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
