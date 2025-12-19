import { useStore } from '../store';
import { TransformWrapper, TransformComponent, useControls } from 'react-zoom-pan-pinch';
import { useEffect } from 'react';

export function Canvas() {
    const { nets, selectedPrimitiveId, selectPrimitive } = useStore();

    // Calculate bounding box
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    // Filter out sentinel points
    const SENTINEL_Y = 1.7976931348623157e+308;

    nets.forEach(net => {
        net.primitives.forEach(p => {
            p.points.forEach(pt => {
                const x = pt[0];
                const y = pt[1];
                if (Math.abs(y - SENTINEL_Y) < 1e20) return; // Skip sentinel
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            });
        });
    });

    if (minX === Infinity) {
        minX = 0; maxX = 0.1; minY = 0; maxY = 0.1;
    }

    const width = maxX - minX;
    const height = maxY - minY;
    // Add some padding
    const paddingX = width * 0.1 || 0.01;
    const paddingY = height * 0.1 || 0.01;

    // PCB tools usually have Y up. SVG has Y down.
    // We use transform="scale(1, -1)" to flip Y.
    // This maps y to -y.
    // If data y is [minY, maxY], mapped y is [-maxY, -minY].
    // The viewBox must cover this mapped range.
    // Top-left of viewBox (in mapped space) is minX, -maxY.

    const viewBox = `${minX - paddingX} ${-maxY - paddingY} ${width + paddingX * 2} ${height + paddingY * 2}`;

    // Helper to create path string
    const createPath = (points: number[][]) => {
        if (points.length === 0) return '';

        let d = '';
        let first = true;

        for (let i = 0; i < points.length; i++) {
            const pt = points[i];
            // Check for sentinel
            if (Math.abs(pt[1] - SENTINEL_Y) < 1e20) {
                continue;
            }

            if (first) {
                d += `M ${pt[0]} ${pt[1]} `;
                first = false;
            } else {
                d += `L ${pt[0]} ${pt[1]} `;
            }
        }
        return d;
    };

    const AutoFit = () => {
        const { resetTransform } = useControls();
        useEffect(() => {
            if (nets.length > 0) {
                resetTransform();
            }
        }, [nets, resetTransform]);
        return null;
    };

    return (
        <div className="canvas-container">
            <TransformWrapper
                initialScale={1}
                minScale={0.1}
                maxScale={10000}
                centerOnInit={true}
            >
                {() => (
                    <>
                        <AutoFit />
                        <TransformComponent wrapperStyle={{ width: '100%', height: '100%' }}>
                            <svg viewBox={viewBox} style={{ width: '100%', height: '100%' }}>
                                <g transform="scale(1, -1)">
                                    {nets.map(net => (
                                        <g key={net.name}>
                                            {net.primitives.map(p => (
                                                <path
                                                    key={p.id}
                                                    d={createPath(p.points)}
                                                    stroke={selectedPrimitiveId === p.id ? '#00ff00' : '#007acc'}
                                                    strokeWidth="2px"
                                                    fill="none"
                                                    vectorEffect="non-scaling-stroke"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        selectPrimitive(p.id);
                                                    }}
                                                    style={{ cursor: 'pointer' }}
                                                >
                                                    <title>{net.name} (ID: {p.id})</title>
                                                </path>
                                            ))}
                                        </g>
                                    ))}
                                </g>
                            </svg>
                        </TransformComponent>
                    </>
                )}
            </TransformWrapper>
            {nets.length === 0 && <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: '#666' }}>No EDB loaded</div>}
        </div>
    );
}
