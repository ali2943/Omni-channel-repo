import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Dashboard', emoji: '📊' },
  { to: '/tickets', label: 'Tickets', emoji: '🎫' },
  { to: '/agents', label: 'Agents', emoji: '👥' },
  { to: '/ai-agents', label: 'AI Agents', emoji: '🤖' },
  { to: '/routing', label: 'Routing Queue', emoji: '📋' },
  { to: '/simulate', label: 'Simulate', emoji: '🧪' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen flex-shrink-0">
      <div className="px-6 py-5 border-b border-gray-700">
        <h1 className="text-xl font-bold tracking-tight">Omni-Channel</h1>
        <p className="text-xs text-gray-400 mt-1">Contact Center</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, emoji }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`
            }
          >
            <span>{emoji}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
