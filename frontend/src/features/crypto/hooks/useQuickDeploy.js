import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from "@/lib/api";

/**
 * Hook to perform an instantaneous S1 (Alpha/Momentum) agent deployment.
 */
export function useQuickDeploy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (symbol) => {
      const params = {
        nombre: `${symbol}-AUTODEPLOY-${Date.now().toString().slice(-4)}`,
        estrategia: 'S1',
        presupuesto: 1000.0,
        umbral: 0.15,
      };

      return api.post('/agents/', null, { params });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['market-data'] });
      console.log('[QUICK DEPLOY] Success: Agent spawned');
    },
    onError: (error) => {
      console.error('[QUICK DEPLOY] Failed:', error.message);
    }
  });
}
