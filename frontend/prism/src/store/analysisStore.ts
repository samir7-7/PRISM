import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AnalyzeResponse, AnalysisState } from '../types';

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      currentAnalysis: null,
      isLoading: false,
      error: null,
      
      setAnalysis: (analysis: AnalyzeResponse | null) =>
        set({ currentAnalysis: analysis, error: null }),
      
      setLoading: (loading: boolean) =>
        set({ isLoading: loading }),
      
      setError: (error: string | null) =>
        set({ error, isLoading: false }),
      
      clearAnalysis: () =>
        set({ currentAnalysis: null, error: null, isLoading: false }),
    }),
    {
      name: 'prism-analysis-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist the analysis data, not loading/error states
      partialize: (state) => ({ currentAnalysis: state.currentAnalysis }),
    }
  )
);

// Made with Bob
