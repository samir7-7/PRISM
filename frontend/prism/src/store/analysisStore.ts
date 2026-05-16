import { create } from 'zustand';
import type { AnalyzeResponse, AnalysisState } from '../types';

export const useAnalysisStore = create<AnalysisState>((set) => ({
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
}));

// Made with Bob
