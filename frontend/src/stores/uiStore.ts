import { create } from 'zustand';
import { EvidenceFactor } from '../types';

interface EvidenceDrawerData {
  title: string;
  moduleName?: string;
  confidence: number;
  value?: any;
  evidence: EvidenceFactor[];
}

interface UIState {
  selectedMissionId: string;
  setSelectedMissionId: (id: string) => void;

  // Evidence Drawer
  isDrawerOpen: boolean;
  drawerData: EvidenceDrawerData | null;
  openEvidenceDrawer: (data: EvidenceDrawerData) => void;
  closeEvidenceDrawer: () => void;

  // Contestability Modal
  contestingItem: { id: string; context: string } | null;
  setContestingItem: (item: { id: string; context: string } | null) => void;

  // Active Scenario Tag Filter
  activeScenarioFilter: string | null;
  setActiveScenarioFilter: (scenario: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  selectedMissionId: 'MIS-101', // Default false idle scenario mission
  setSelectedMissionId: (id: string) => set({ selectedMissionId: id }),

  isDrawerOpen: false,
  drawerData: null,
  openEvidenceDrawer: (data: EvidenceDrawerData) =>
    set({ isDrawerOpen: true, drawerData: data }),
  closeEvidenceDrawer: () => set({ isDrawerOpen: false, drawerData: null }),

  contestingItem: null,
  setContestingItem: (item) => set({ contestingItem: item }),

  activeScenarioFilter: null,
  setActiveScenarioFilter: (scenario) => set({ activeScenarioFilter: scenario }),
}));
