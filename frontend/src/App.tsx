import { useState } from 'react';
import './App.css';
import { useStore } from './store';
import { SettingsPanel } from './components/SettingsPanel';
import { NetsPanel } from './components/NetsPanel';
import { Canvas } from './components/Canvas';
import { StatsPanel } from './components/StatsPanel';
import { Save, FolderOpen, Play } from 'lucide-react';

// Define the API interface
declare global {
  interface Window {
    pywebview: {
      api: {
        greet: () => Promise<string>;
        open_file_dialog: () => Promise<string | null>;
        save_file_dialog: () => Promise<string | null>;
        load_edb: (path: string) => Promise<{ nets: any[] } | { error: string }>;
        save_edb: (path: string) => Promise<boolean>;
        generate_variation: (settings: any) => Promise<boolean>;
        get_primitive_stats: (id: string | number) => Promise<{ s: number[], w_s: number[] } | null>;
        get_nets: () => Promise<{ nets: any[] }>;
      };
    };
  }
}

function App() {
  const { setNets, settings, selectedPrimitiveId, setVariationStats } = useStore();
  const [loading, setLoading] = useState(false);

  const handleOpen = async () => {
    if (!window.pywebview) return;
    const path = await window.pywebview.api.open_file_dialog();
    if (path) {
      setLoading(true);
      const data = await window.pywebview.api.load_edb(path);
      setLoading(false);
      if ('nets' in data) {
        setNets(data.nets);
      } else {
        alert('Error loading EDB: ' + data.error);
      }
    }
  };

  const handleSave = async () => {
    if (!window.pywebview) return;
    const path = await window.pywebview.api.save_file_dialog();
    if (path) {
      setLoading(true);
      await window.pywebview.api.save_edb(path);
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!window.pywebview) return;
    setLoading(true);
    const success = await window.pywebview.api.generate_variation(settings);
    if (success) {
      if (window.pywebview.api.get_nets) {
        const data = await window.pywebview.api.get_nets();
        if ('nets' in data) {
          setNets(data.nets);
        }
      }

      // Refresh stats if a primitive is selected
      if (selectedPrimitiveId) {
        const stats = await window.pywebview.api.get_primitive_stats(selectedPrimitiveId);
        setVariationStats(stats as { s: number[], w_s: number[], mu_w: number } | null);
      }
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">Line Width Variator</div>
        <div className="toolbar">
          <button onClick={handleOpen}><FolderOpen size={16} /> Open</button>
          <button onClick={handleSave}><Save size={16} /> Save As</button>
          <button onClick={handleGenerate} className="primary"><Play size={16} /> Generate</button>
        </div>
      </header>
      <div className="main-content">
        <aside className="left-panel">
          <SettingsPanel />
        </aside>
        <main className="center-panel">
          <Canvas />
          <StatsPanel />
        </main>
        <aside className="right-panel">
          <NetsPanel />
        </aside>
      </div>
      {loading && <div className="loading-overlay">Processing...</div>}
    </div>
  );
}

export default App;
