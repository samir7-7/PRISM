import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { GraphNode, GraphEdge } from '../../types';

interface DependencyGraphProps {
  impactedNodes: string[];
  changedFiles: string[];
}

const nodeTypes = {
  custom: ({ data }: any) => (
    <div
      className={`px-4 py-3 rounded border-2 bg-prism-surface min-w-[180px] ${
        data.type === 'source'
          ? 'border-prism-orange'
          : data.type === 'impacted'
          ? 'border-prism-orange/60'
          : 'border-prism-border'
      }`}
    >
      <div className="text-xs text-prism-text-muted mb-1">{data.service}</div>
      <div className={`text-sm font-mono font-semibold ${
        data.type === 'nominal' ? 'text-prism-text-muted' : 'text-prism-text'
      }`}>
        {data.method}
      </div>
      <div className={`text-xs mt-1 ${
        data.type === 'source' 
          ? 'text-prism-orange' 
          : data.type === 'impacted'
          ? 'text-prism-orange/80'
          : 'text-prism-text-muted'
      }`}>
        {data.status}
      </div>
    </div>
  ),
};

export const DependencyGraph = ({ impactedNodes, changedFiles }: DependencyGraphProps) => {
  // Parse nodes from impacted_nodes array
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    
    // Create nodes from impacted_nodes
    impactedNodes.forEach((nodeStr, index) => {
      const parts = nodeStr.split('.');
      const service = parts[0] || 'unknown';
      const method = parts.slice(1).join('.') || 'main';
      
      // Determine node type
      let type: 'source' | 'impacted' | 'nominal' = 'nominal';
      let status = 'Nominal';
      
      if (index === 0 || changedFiles.some(f => f.includes(service))) {
        type = 'source';
        status = 'Source of Drift';
      } else if (index < impactedNodes.length / 2) {
        type = 'impacted';
        status = 'Impacted';
      }
      
      nodes.push({
        id: `node-${index}`,
        type: 'custom',
        position: { 
          x: (index % 3) * 250 + 50, 
          y: Math.floor(index / 3) * 150 + 50 
        },
        data: {
          label: nodeStr,
          service,
          method,
          type,
          status,
        },
      });
      
      // Create edges (connect sequential nodes)
      if (index > 0) {
        edges.push({
          id: `edge-${index}`,
          source: `node-${index - 1}`,
          target: `node-${index}`,
          type: 'smoothstep',
          animated: type === 'impacted' || type === 'source',
          style: { 
            stroke: type === 'impacted' || type === 'source' ? '#f97316' : '#21262d',
            strokeWidth: 2,
          },
        });
      }
    });
    
    return { nodes, edges };
  }, [impactedNodes, changedFiles]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="card h-[600px] relative">
      {/* Header */}
      <div className="absolute top-4 left-4 z-10 bg-prism-surface/90 backdrop-blur px-4 py-2 rounded border border-prism-border">
        <h3 className="text-sm font-semibold text-prism-text">Dependency Graph</h3>
      </div>

      {/* Custom Controls */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <button className="p-2 bg-prism-surface border border-prism-border rounded hover:bg-prism-bg transition-colors">
          <ZoomIn className="w-4 h-4 text-prism-text" />
        </button>
        <button className="p-2 bg-prism-surface border border-prism-border rounded hover:bg-prism-bg transition-colors">
          <ZoomOut className="w-4 h-4 text-prism-text" />
        </button>
        <button className="p-2 bg-prism-surface border border-prism-border rounded hover:bg-prism-bg transition-colors">
          <Maximize2 className="w-4 h-4 text-prism-text" />
        </button>
      </div>

      {/* React Flow */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        className="bg-prism-bg"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#21262d" gap={16} />
        <Controls className="bg-prism-surface border-prism-border" />
        <MiniMap 
          className="bg-prism-surface border border-prism-border"
          nodeColor={(node) => {
            if (node.data.type === 'source') return '#f97316';
            if (node.data.type === 'impacted') return '#f97316';
            return '#21262d';
          }}
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-prism-surface/90 backdrop-blur px-4 py-3 rounded border border-prism-border">
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-prism-orange"></div>
            <span className="text-prism-text-muted">POTENTIAL BREAK</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-prism-border"></div>
            <span className="text-prism-text-muted">NOMINAL</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-4 right-4 z-10 bg-prism-surface/90 backdrop-blur px-4 py-2 rounded border border-prism-border flex items-center gap-4 text-xs text-prism-text-muted">
        <span>SCHEMA V2.4.1</span>
        <span className="text-prism-green">AUTO-SAVE ENABLED ✓</span>
      </div>
    </div>
  );
};

// Made with Bob
