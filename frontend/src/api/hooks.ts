// React Query hooks for data fetching

import { useQuery, useQueries } from '@tanstack/react-query';
import { api } from './client';

export function useJobsIndex() {
  return useQuery({
    queryKey: ['jobs', 'index'],
    queryFn: api.getJobsIndex,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useJobsPage(page: number) {
  return useQuery({
    queryKey: ['jobs', 'page', page],
    queryFn: () => api.getJobsPage(page),
    staleTime: 1000 * 60 * 60,
  });
}

export function useJobsPages(pages: number[]) {
  return useQueries({
    queries: pages.map(page => ({
      queryKey: ['jobs', 'page', page],
      queryFn: () => api.getJobsPage(page),
      staleTime: 1000 * 60 * 60,
    })),
  });
}

export function useJobDetail(jobId: number) {
  return useQuery({
    queryKey: ['jobs', 'detail', jobId],
    queryFn: () => api.getJobDetail(jobId),
    staleTime: 1000 * 60 * 60,
    enabled: !!jobId,
  });
}

export function useAnalysisIndex() {
  return useQuery({
    queryKey: ['analysis', 'index'],
    queryFn: api.getAnalysisIndex,
    staleTime: 1000 * 60 * 60,
  });
}

export function useAnalysis(endpoint: string) {
  return useQuery({
    queryKey: ['analysis', endpoint],
    queryFn: () => api.getAnalysis(endpoint),
    staleTime: 1000 * 60 * 60,
    enabled: !!endpoint,
  });
}
