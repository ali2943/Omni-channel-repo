import { useState } from 'react';
import {
  simulateEmail,
  simulateWhatsApp,
  simulateSocial,
  simulateVoice,
  simulateShopify,
  simulateWebchat,
} from '../api';

type TabKey = 'email' | 'whatsapp' | 'social' | 'voice' | 'shopify' | 'webchat';

const tabs: { key: TabKey; label: string; emoji: string }[] = [
  { key: 'email', label: 'Email', emoji: '📧' },
  { key: 'whatsapp', label: 'WhatsApp', emoji: '💬' },
  { key: 'social', label: 'Social', emoji: '📱' },
  { key: 'voice', label: 'Voice', emoji: '📞' },
  { key: 'shopify', label: 'Shopify', emoji: '🛒' },
  { key: 'webchat', label: 'WebChat', emoji: '🌐' },
];

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {children}
    </div>
  );
}

const inputCls =
  'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500';

export default function Simulate() {
  const [activeTab, setActiveTab] = useState<TabKey>('email');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; msg: string } | null>(null);

  // Form fields
  const [emailForm, setEmailForm] = useState({
    customer_name: '',
    customer_email: '',
    subject: '',
    body: '',
  });
  const [whatsappForm, setWhatsappForm] = useState({
    customer_name: '',
    customer_phone: '',
    message: '',
  });
  const [socialForm, setSocialForm] = useState({
    platform: 'facebook',
    customer_handle: '',
    message: '',
  });
  const [voiceForm, setVoiceForm] = useState({
    customer_name: '',
    customer_phone: '',
    notes: '',
  });
  const [shopifyForm, setShopifyForm] = useState({
    customer_name: '',
    customer_email: '',
    order_id: '',
    issue: '',
  });
  const [webchatForm, setWebchatForm] = useState({
    customer_name: '',
    customer_email: '',
    message: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setResult(null);
    try {
      let res: { ticket_id: number };
      if (activeTab === 'email') res = await simulateEmail(emailForm);
      else if (activeTab === 'whatsapp') res = await simulateWhatsApp(whatsappForm);
      else if (activeTab === 'social') res = await simulateSocial(socialForm);
      else if (activeTab === 'voice') res = await simulateVoice(voiceForm);
      else if (activeTab === 'shopify') res = await simulateShopify(shopifyForm);
      else res = await simulateWebchat(webchatForm);
      setResult({ ok: true, msg: `✅ Ticket created: ${res.ticket_id}` });
    } catch {
      setResult({ ok: false, msg: '❌ Simulation failed. Check that the backend is running.' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Simulate Incoming Contact</h2>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 flex-wrap">
        {tabs.map(({ key, label, emoji }) => (
          <button
            key={key}
            onClick={() => {
              setActiveTab(key);
              setResult(null);
            }}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === key
                ? 'bg-white shadow text-gray-900'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {emoji} {label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-w-lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          {activeTab === 'email' && (
            <>
              <Field label="Customer Name">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={emailForm.customer_name}
                  onChange={(e) => setEmailForm((f) => ({ ...f, customer_name: e.target.value }))}
                />
              </Field>
              <Field label="Customer Email">
                <input
                  required
                  type="email"
                  className={inputCls}
                  value={emailForm.customer_email}
                  onChange={(e) => setEmailForm((f) => ({ ...f, customer_email: e.target.value }))}
                />
              </Field>
              <Field label="Subject">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={emailForm.subject}
                  onChange={(e) => setEmailForm((f) => ({ ...f, subject: e.target.value }))}
                />
              </Field>
              <Field label="Body">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={emailForm.body}
                  onChange={(e) => setEmailForm((f) => ({ ...f, body: e.target.value }))}
                />
              </Field>
            </>
          )}

          {activeTab === 'whatsapp' && (
            <>
              <Field label="Customer Name">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={whatsappForm.customer_name}
                  onChange={(e) =>
                    setWhatsappForm((f) => ({ ...f, customer_name: e.target.value }))
                  }
                />
              </Field>
              <Field label="Customer Phone">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={whatsappForm.customer_phone}
                  onChange={(e) =>
                    setWhatsappForm((f) => ({ ...f, customer_phone: e.target.value }))
                  }
                />
              </Field>
              <Field label="Message">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={whatsappForm.message}
                  onChange={(e) => setWhatsappForm((f) => ({ ...f, message: e.target.value }))}
                />
              </Field>
            </>
          )}

          {activeTab === 'social' && (
            <>
              <Field label="Platform">
                <select
                  className={inputCls}
                  value={socialForm.platform}
                  onChange={(e) => setSocialForm((f) => ({ ...f, platform: e.target.value }))}
                >
                  <option value="facebook">Facebook</option>
                  <option value="instagram">Instagram</option>
                  <option value="tiktok">TikTok</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
              </Field>
              <Field label="Customer Handle">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={socialForm.customer_handle}
                  onChange={(e) =>
                    setSocialForm((f) => ({ ...f, customer_handle: e.target.value }))
                  }
                />
              </Field>
              <Field label="Message">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={socialForm.message}
                  onChange={(e) => setSocialForm((f) => ({ ...f, message: e.target.value }))}
                />
              </Field>
            </>
          )}

          {activeTab === 'voice' && (
            <>
              <Field label="Customer Name">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={voiceForm.customer_name}
                  onChange={(e) => setVoiceForm((f) => ({ ...f, customer_name: e.target.value }))}
                />
              </Field>
              <Field label="Customer Phone">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={voiceForm.customer_phone}
                  onChange={(e) =>
                    setVoiceForm((f) => ({ ...f, customer_phone: e.target.value }))
                  }
                />
              </Field>
              <Field label="Notes">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={voiceForm.notes}
                  onChange={(e) => setVoiceForm((f) => ({ ...f, notes: e.target.value }))}
                />
              </Field>
            </>
          )}

          {activeTab === 'shopify' && (
            <>
              <Field label="Customer Name">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={shopifyForm.customer_name}
                  onChange={(e) =>
                    setShopifyForm((f) => ({ ...f, customer_name: e.target.value }))
                  }
                />
              </Field>
              <Field label="Customer Email">
                <input
                  required
                  type="email"
                  className={inputCls}
                  value={shopifyForm.customer_email}
                  onChange={(e) =>
                    setShopifyForm((f) => ({ ...f, customer_email: e.target.value }))
                  }
                />
              </Field>
              <Field label="Order ID">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={shopifyForm.order_id}
                  onChange={(e) => setShopifyForm((f) => ({ ...f, order_id: e.target.value }))}
                />
              </Field>
              <Field label="Issue">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={shopifyForm.issue}
                  onChange={(e) => setShopifyForm((f) => ({ ...f, issue: e.target.value }))}
                />
              </Field>
            </>
          )}

          {activeTab === 'webchat' && (
            <>
              <Field label="Customer Name">
                <input
                  required
                  type="text"
                  className={inputCls}
                  value={webchatForm.customer_name}
                  onChange={(e) =>
                    setWebchatForm((f) => ({ ...f, customer_name: e.target.value }))
                  }
                />
              </Field>
              <Field label="Customer Email">
                <input
                  required
                  type="email"
                  className={inputCls}
                  value={webchatForm.customer_email}
                  onChange={(e) =>
                    setWebchatForm((f) => ({ ...f, customer_email: e.target.value }))
                  }
                />
              </Field>
              <Field label="Message">
                <textarea
                  required
                  rows={3}
                  className={inputCls}
                  value={webchatForm.message}
                  onChange={(e) => setWebchatForm((f) => ({ ...f, message: e.target.value }))}
                />
              </Field>
            </>
          )}

          {result && (
            <div
              className={`text-sm rounded-lg px-4 py-3 ${
                result.ok
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {result.msg}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm"
          >
            {submitting ? 'Submitting…' : 'Simulate'}
          </button>
        </form>
      </div>
    </div>
  );
}
