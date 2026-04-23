import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/shared/lib/api-client';

/**
 * Hook to perform an instantaneous agent deployment
 */
export function useQuickDeploy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (symbol) => {
      const payload = {
        name: `${symbol}-AUTODEPLOY-${Date.now().toString().slice(-4)}`,
        agent_type: 'crypto_trader',
        initial_capital: 1000.0,
        specialization: [symbol],
        config: {
          mode: 'test',
          quick_deploy: true
        }
      };

      return api.post('/agents/', payload);
    },
    onSuccess: () => {
      // Invalidate agents list to show the new one
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['market-data'] });
      console.log('[QUICK DEPLOY] Success: Agent spawned');
    },
    onError: (error) => {
      console.error('[QUICK DEPLOY] Failed:', error.message);
    }
  });
}
