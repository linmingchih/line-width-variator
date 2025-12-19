import { useState } from 'react';
import { useStore } from '../store';

export function NetsPanel() {
    const { nets, selectedPrimitiveId, selectPrimitive } = useStore();
    const [filter, setFilter] = useState('');

    const filteredNets = nets.filter(net =>
        net.name.toLowerCase().includes(filter.toLowerCase()) ||
        net.primitives.some(p => p.id.toString().includes(filter))
    );

    return (
        <>
            <div className="panel-header">Nets</div>
            <div style={{ padding: '8px' }}>
                <input
                    type="text"
                    placeholder="Filter nets..."
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                    style={{ width: '100%', padding: '4px', background: '#3c3c3c', border: '1px solid #3e3e42', color: 'white' }}
                />
            </div>
            <div className="nets-content">
                {filteredNets.map(net => (
                    <div key={net.name}>
                        <div className="net-item">{net.name}</div>
                        {net.primitives.map(p => (
                            <div
                                key={p.id}
                                className={`primitive-item ${selectedPrimitiveId === p.id ? 'selected' : ''}`}
                                onClick={() => selectPrimitive(p.id)}
                            >
                                Path {p.id} ({p.layer})
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </>
    );
}
