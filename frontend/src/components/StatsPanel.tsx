import { useEffect, useState } from 'react';
import { useStore } from '../store';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function StatsPanel() {
    const { selectedPrimitiveId, variationStats, setVariationStats } = useStore();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchStats = async () => {
            if (selectedPrimitiveId && window.pywebview) {
                setLoading(true);
                const stats = await window.pywebview.api.get_primitive_stats(selectedPrimitiveId);
                setVariationStats(stats);
                setLoading(false);
            } else {
                setVariationStats(null);
            }
        };

        fetchStats();
    }, [selectedPrimitiveId, setVariationStats]);

    if (!selectedPrimitiveId) {
        return <div className="stats-panel"><div className="stats-content">Select a primitive to view stats</div></div>;
    }

    if (loading) {
        return <div className="stats-panel"><div className="stats-content">Loading stats...</div></div>;
    }

    if (!variationStats) {
        return <div className="stats-panel"><div className="stats-content">No variation data available for this primitive. Generate variation first.</div></div>;
    }

    // Transform data for Recharts
    const data = variationStats.s.map((s, i) => ({
        s: s,
        width: variationStats.w_s[i]
    }));

    return (
        <div className="stats-panel">
            <div className="panel-header">Statistics - Primitive {selectedPrimitiveId}</div>
            <div className="stats-content">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                        <XAxis dataKey="s" stroke="#888" label={{ value: 'Path Length', position: 'insideBottom', offset: -5 }} />
                        <YAxis stroke="#888" label={{ value: 'Width', angle: -90, position: 'insideLeft' }} />
                        <Tooltip contentStyle={{ backgroundColor: '#333', border: '1px solid #555' }} />
                        <Line type="monotone" dataKey="width" stroke="#007acc" dot={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
