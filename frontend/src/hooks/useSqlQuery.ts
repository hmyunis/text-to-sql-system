import { useMutation, useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export const useSqlQuery = () => {
  const askMutation = useMutation({
    mutationFn: async (question: string) => {
      const { data } = await axios.post(`${API_BASE}/ask/`, { question });
      return data;
    },
  });

  const schemaQuery = useQuery({
    queryKey: ['schema'],
    queryFn: async () => {
      const { data } = await axios.get(`${API_BASE}/schema/`);
      return data.schema;
    },
  });

  return { askMutation, schemaQuery };
};
