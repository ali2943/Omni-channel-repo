import { useEffect, useState } from 'react';
import { getKPIs, getVolume } from '../api';
import type { KPI, VolumeEntry } from '../api';

const channelEmoji: Record<string, string> = {
  email: '📧',
  whatsapp: '💬',
  social: '📱',
  voice: '📞',
  shopify: '🛒',
  webchat: '🌐',
};

function KPICard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <p className="text-sm text-gray-500 font-medium">{label}</p>
      <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPI | null>(null);
  const [volume, setVolume] = useState<VolumeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiData, volumeData] = await Promise.all([getKPIs(), getVolume()]);
        setKpis(kpiData);
        setVolume(volumeData);
      } catch (err) {
        console.error('Failed to load analytics data:', err);
        setError('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
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
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h2>

      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <KPICard label="Total Tickets" value={kpis.total_tickets} />
          <KPICard label="Open" value={kpis.open_tickets} />
          <KPICard label="In Progress" value={kpis.in_progress_tickets} />
          <KPICard label="Closed" value={kpis.closed_tickets} />
          <KPICard
            label="SLA Compliance"
            value={`${kpis.sla_compliance_percentage.toFixed(1)}%`}
          />
          <KPICard
            label="Avg Handle Time"
            value={`${kpis.average_handle_time_minutes.toFixed(0)} min`}
          />
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Ticket Volume by Channel</h3>
        {volume.length === 0 ? (
          <p className="text-gray-500 text-sm">No volume data available.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Channel</th>
                <th className="pb-2 font-medium text-right">Tickets</th>
              </tr>
            </thead>
            <tbody>
              {volume.map((entry) => (
                <tr key={entry.channel} className="border-b last:border-0">
                  <td className="py-3">
                    <span className="mr-2">{channelEmoji[entry.channel] ?? '📌'}</span>
                    <span className="capitalize">{entry.channel}</span>
                  </td>
                  <td className="py-3 text-right font-semibold">{entry.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
