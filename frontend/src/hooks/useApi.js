import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { dataService, scraperService, authService, healthService } from '../services/api';

// Hook pour récupérer les projets avec filtres et pagination
export const useProjects = (params = {}, options = {}) => {
  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => dataService.getProjects(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (remplace cacheTime)
    ...options
  });
};

// Hook pour récupérer un projet spécifique
export const useProject = (id, options = {}) => {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => dataService.getProject(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    ...options
  });
};

// Hook pour récupérer les données filtrées
export const useFilteredData = (filterType, params = {}, options = {}) => {
  return useQuery({
    queryKey: ['filteredData', filterType, params],
    queryFn: () => dataService.getFilteredData(filterType, params),
    enabled: !!filterType,
    staleTime: 5 * 60 * 1000,
    ...options
  });
};

// Hook pour récupérer les statistiques
export const useStatistics = (options = {}) => {
  return useQuery({
    queryKey: ['statistics'],
    queryFn: () => dataService.getStatistics(),
    staleTime: 15 * 60 * 1000, // 15 minutes pour les stats
    gcTime: 30 * 60 * 1000, // 30 minutes
    ...options
  });
};

// Hook pour récupérer les métadonnées
export const useMetadata = (options = {}) => {
  return useQuery({
    queryKey: ['metadata'],
    queryFn: () => dataService.getMetadata(),
    staleTime: 30 * 60 * 1000, // 30 minutes pour les métadonnées
    gcTime: 60 * 60 * 1000, // 1 heure
    ...options
  });
};

// Hook pour le statut du scraper
export const useScraperStatus = (options = {}) => {
  return useQuery({
    queryKey: ['scraperStatus'],
    queryFn: () => scraperService.getStatus(),
    refetchInterval: 5000, // Actualiser toutes les 5 secondes
    staleTime: 0, // Toujours considérer comme périmé
    ...options
  });
};

// Hook pour vérifier la santé de l'API
export const useHealth = (options = {}) => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => healthService.check(),
    refetchInterval: 30000, // Vérifier toutes les 30 secondes
    staleTime: 0,
    retry: 1,
    ...options
  });
};

// Hook pour l'authentification
export const useAuth = () => {
  const queryClient = useQueryClient();
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('authToken');
  });

  const loginMutation = useMutation({
    mutationFn: (credentials) => authService.login(credentials),
    onSuccess: (data) => {
      if (data.success && data.data.token) {
        localStorage.setItem('authToken', data.data.token);
        setIsAuthenticated(true);
        toast.success('Connexion réussie!');
        queryClient.invalidateQueries(); // Invalider toutes les requêtes
      }
    },
    onError: (error) => {
      toast.error(`Erreur de connexion: ${error.response?.data?.error?.message || error.message || 'Erreur inconnue'}`);
    }
  });

  const logout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    queryClient.clear(); // Vider le cache
    toast.info('Déconnexion réussie');
  };

  return {
    login: loginMutation.mutate,
    logout,
    isLoading: loginMutation.isPending, // isPending remplace isLoading dans v5
    isAuthenticated,
    error: loginMutation.error
  };
};

// Hook pour déclencher le scraper
export const useScraper = () => {
  const queryClient = useQueryClient();

  const triggerMutation = useMutation({
    mutationFn: () => scraperService.trigger(),
    onSuccess: () => {
      toast.success('Scraper démarré avec succès!');
      queryClient.invalidateQueries({ queryKey: ['scraperStatus'] });
      // Invalider les données après un délai pour laisser le temps au scraper
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['projects'] });
        queryClient.invalidateQueries({ queryKey: ['statistics'] });
      }, 5000);
    },
    onError: (error) => {
      const errorData = error.response?.data?.error;
      if (errorData?.code === 'SCRAPER_BUSY') {
        toast.warning('Le scraper est déjà en cours d\'exécution');
      } else {
        toast.error(`Erreur lors du démarrage du scraper: ${errorData?.message || error.message || 'Erreur inconnue'}`);
      }
    }
  });

  const resetLimitsMutation = useMutation({
    mutationFn: () => scraperService.resetLimits(),
    onSuccess: () => {
      toast.success('Limites de taux réinitialisées!');
    },
    onError: (error) => {
      const errorData = error.response?.data?.error;
      toast.error(`Erreur lors de la réinitialisation: ${errorData?.message || error.message || 'Erreur inconnue'}`);
    }
  });

  return {
    trigger: triggerMutation.mutate,
    isLoading: triggerMutation.isPending,
    error: triggerMutation.error,
    resetLimits: resetLimitsMutation.mutate,
    isResettingLimits: resetLimitsMutation.isPending
  };
};

// Hook pour la recherche avec debounce
export const useSearch = (searchTerm, delay = 500) => {
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, delay]);

  return useProjects(
    { search: debouncedTerm, limit: 10 },
    { enabled: debouncedTerm.length > 2 }
  );
};

// Hook pour la pagination
export const usePagination = (initialPage = 1, initialLimit = 20) => {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);

  const resetPagination = () => {
    setPage(1);
  };

  const nextPage = () => setPage(prev => prev + 1);
  const prevPage = () => setPage(prev => Math.max(1, prev - 1));
  const goToPage = (pageNumber) => setPage(Math.max(1, pageNumber));

  return {
    page,
    limit,
    setPage,
    setLimit,
    resetPagination,
    nextPage,
    prevPage,
    goToPage
  };
}; 