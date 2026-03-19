import { create } from "zustand";
import type { ScanResult, ScanHistoryItem } from "./api";

interface AppState {
  currentScan: ScanResult | null;
  scanHistory: ScanHistoryItem[];
  logs: string[];
  isAuthenticated: boolean;
  userEmail: string | null;

  setCurrentScan: (scan: ScanResult | null) => void;
  setScanHistory: (history: ScanHistoryItem[]) => void;
  addLog: (log: string) => void;
  clearLogs: () => void;
  setAuth: (isAuth: boolean, email?: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentScan: null,
  scanHistory: [],
  logs: [],
  isAuthenticated: false,
  userEmail: null,

  setCurrentScan: (scan) => set({ currentScan: scan }),
  setScanHistory: (history) => set({ scanHistory: history }),
  addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
  clearLogs: () => set({ logs: [] }),
  setAuth: (isAuth, email) =>
    set({ isAuthenticated: isAuth, userEmail: email ?? null }),
}));
