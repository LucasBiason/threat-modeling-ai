import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAnalysis } from '../services/threatModelingService';

export function useCreateAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const create = useCallback(async () => {
    if (!file) {
      setError('Selecione um arquivo primeiro');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await createAnalysis(file);
      navigate(`/analyses/${result.id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Falha ao enviar análise';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [file, navigate]);

  return { file, loading, error, setFile, createAnalysis: create };
}
