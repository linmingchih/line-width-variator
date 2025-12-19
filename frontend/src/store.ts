import { create } from 'zustand';

interface Primitive {
    id: string | number;
    type: string;
    layer: string;
    width: number;
    points: number[][];
}

interface Net {
    name: string;
    primitives: Primitive[];
}

interface Settings {
    sigma_w: number;
    L_c: number;
    model: string;
    ds_arc: number;
    n_resample: number;
    w_min: number;
    w_max: number;
}

interface AppState {
    nets: Net[];
    selectedPrimitiveId: string | number | null;
    settings: Settings;
    variationStats: { s: number[], w_s: number[], mu_w: number } | null;

    setNets: (nets: Net[]) => void;
    selectPrimitive: (id: string | number | null) => void;
    updateSettings: (settings: Partial<Settings>) => void;
    setVariationStats: (stats: { s: number[], w_s: number[], mu_w: number } | null) => void;
}

export const useStore = create<AppState>((set) => ({
    nets: [],
    selectedPrimitiveId: null,
    settings: {
        sigma_w: 10,
        L_c: 0.002,
        model: 'matern32',
        ds_arc: 2e-4,
        n_resample: 1200,
        w_min: 80,
        w_max: 120
    },
    variationStats: null,

    setNets: (nets) => set({ nets }),
    selectPrimitive: (id) => set({ selectedPrimitiveId: id }),
    updateSettings: (newSettings) => set((state) => ({ settings: { ...state.settings, ...newSettings } })),
    setVariationStats: (stats) => set({ variationStats: stats }),
}));
