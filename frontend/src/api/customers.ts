import client from './client';
import type { Customer } from './types';

export const getCustomer = async (id: number): Promise<Customer> => {
  const { data } = await client.get(`/customers/${id}`);
  return data;
};

export const createCustomer = async (payload: {
  name: string;
  email: string;
  phone?: string;
}): Promise<Customer> => {
  const { data } = await client.post('/customers/', payload);
  return data;
};
