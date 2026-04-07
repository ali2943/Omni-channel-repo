import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Tickets from './pages/Tickets';
import TicketDetail from './pages/TicketDetail';
import Agents from './pages/Agents';
import RoutingQueue from './pages/RoutingQueue';
import Simulate from './pages/Simulate';

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/tickets/:id" element={<TicketDetail />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/routing" element={<RoutingQueue />} />
            <Route path="/simulate" element={<Simulate />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
