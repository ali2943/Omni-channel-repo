import client from './client';

interface SimulateResult {
  ticket_id: number;
}

export const simulateEmail = async (payload: {
  customer_name: string;
  customer_email: string;
  subject: string;
  body: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/email', payload);
  return data;
};

export const simulateWhatsApp = async (payload: {
  customer_name: string;
  customer_phone: string;
  message: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/whatsapp', payload);
  return data;
};

export const simulateSocial = async (payload: {
  platform: string;
  customer_handle: string;
  message: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/social', payload);
  return data;
};

export const simulateVoice = async (payload: {
  customer_name: string;
  customer_phone: string;
  notes: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/voice', payload);
  return data;
};

export const simulateShopify = async (payload: {
  customer_name: string;
  customer_email: string;
  order_id: string;
  issue: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/shopify', payload);
  return data;
};

export const simulateWebchat = async (payload: {
  customer_name: string;
  customer_email: string;
  message: string;
}): Promise<SimulateResult> => {
  const { data } = await client.post('/simulate/webchat', payload);
  return data;
};
