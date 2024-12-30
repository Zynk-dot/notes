import { useState, useCallback, useEffect } from 'react';
import { modelService } from '../services/modelService';
import { ModelError } from '../utils/errors';
import { type Note } from '../types';
import { debounce } from '../utils/performance';

export function useModelProcessing() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cleanup resources when component unmounts
  useEffect(() => {
    return () => {
      modelService.dispose();
    };
  }, []);

  const processText = useCallback(
    debounce(async (text: string): Promise<Note | null> => {
      if (!text.trim()) return null;
      
      setIsProcessing(true);
      setError(null);

      try {
        const [summary, bullets] = await Promise.all([
          modelService.summarizeText(text),
          modelService.generateBulletPoints(text)
        ]);

        return {
          id: Date.now().toString(),
          text,
          summary,
          bullets,
          timestamp: new Date()
        };
      } catch (err) {
        const errorMessage = err instanceof ModelError 
          ? err.message 
          : 'An unexpected error occurred';
        setError(errorMessage);
        console.error('Error processing text:', err);
        return null;
      } finally {
        setIsProcessing(false);
      }
    }, 500), // Debounce for 500ms
    []
  );

  return { processText, isProcessing, error };
}