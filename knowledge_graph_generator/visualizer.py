"""
Knowledge Graph Visualizer Module
Creates visual representations of knowledge graphs using various backends.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Node:
    """Represents a node in the knowledge graph."""
    id: str
    label: str
    node_type: str
    size: float = 25
    color: Optional[str] = None
    attributes: Dict = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.color is None:
            self.color = self._get_default_color()

    def _get_default_color(self) -> str:
        """Get default color based on node type."""
        color_map = {
            # Code entities
            'class': '#e74c3c',        # Red
            'function': '#3498db',      # Blue
            'method': '#9b59b6',        # Purple
            'variable': '#2ecc71',      # Green
            'import': '#f39c12',        # Orange
            'module': '#1abc9c',        # Teal
            # Text entities
            'PERSON': '#e74c3c',        # Red
            'ORG': '#3498db',           # Blue
            'GPE': '#2ecc71',           # Green
            'CONCEPT': '#9b59b6',       # Purple
            'NOUN': '#f39c12',          # Orange
            'TECHNICAL': '#1abc9c',     # Teal
            'STRING': '#95a5a6',        # Gray
            # Default
            'default': '#34495e'        # Dark gray
        }
        return color_map.get(self.node_type, color_map['default'])


@dataclass
class Edge:
    """Represents an edge in the knowledge graph."""
    source: str
    target: str
    label: str
    weight: float = 1.0
    color: Optional[str] = None
    attributes: Dict = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.color is None:
            self.color = self._get_default_color()

    def _get_default_color(self) -> str:
        """Get default color based on edge label."""
        color_map = {
            'inherits': '#e74c3c',
            'extends': '#e74c3c',
            'implements': '#c0392b',
            'imports': '#f39c12',
            'calls': '#3498db',
            'uses': '#2ecc71',
            'contains': '#9b59b6',
            'is_a': '#1abc9c',
            'has': '#27ae60',
            'depends_on': '#e67e22',
            'exports': '#16a085',
            'default': '#7f8c8d'
        }
        return color_map.get(self.label, color_map['default'])


class KnowledgeGraph:
    """
    Knowledge Graph data structure and operations.
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        """Add an edge to the graph."""
        # Ensure source and target nodes exist
        if edge.source not in self.nodes:
            self.nodes[edge.source] = Node(
                id=edge.source,
                label=edge.source,
                node_type='default'
            )
        if edge.target not in self.nodes:
            self.nodes[edge.target] = Node(
                id=edge.target,
                label=edge.target,
                node_type='default'
            )
        self.edges.append(edge)

    def to_networkx(self):
        """Convert to NetworkX graph."""
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required. Install with: pip install networkx")

        G = nx.DiGraph()

        for node_id, node in self.nodes.items():
            G.add_node(node_id,
                       label=node.label,
                       node_type=node.node_type,
                       size=node.size,
                       color=node.color,
                       **node.attributes)

        for edge in self.edges:
            G.add_edge(edge.source, edge.target,
                       label=edge.label,
                       weight=edge.weight,
                       color=edge.color,
                       **edge.attributes)

        return G

    def to_json(self) -> Dict:
        """Convert graph to JSON-serializable dictionary."""
        return {
            'nodes': [
                {
                    'id': node.id,
                    'label': node.label,
                    'type': node.node_type,
                    'size': node.size,
                    'color': node.color,
                    **node.attributes
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'label': edge.label,
                    'weight': edge.weight,
                    'color': edge.color,
                    **edge.attributes
                }
                for edge in self.edges
            ]
        }

    def __len__(self):
        return len(self.nodes)


class GraphVisualizer:
    """
    Visualizes knowledge graphs using various backends.
    """

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def to_matplotlib(self, output_path: Optional[str] = None, figsize: Tuple[int, int] = (16, 12)):
        """
        Render graph using matplotlib.

        Args:
            output_path: Path to save the figure (optional)
            figsize: Figure size as (width, height)

        Returns:
            matplotlib figure object
        """
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            raise ImportError("matplotlib and networkx are required. Install with: pip install matplotlib networkx")

        G = self.graph.to_networkx()

        fig, ax = plt.subplots(figsize=figsize)

        # Calculate layout
        if len(G) > 50:
            pos = nx.spring_layout(G, k=2, iterations=50)
        else:
            pos = nx.spring_layout(G, k=3, iterations=100)

        # Get node properties
        node_colors = [G.nodes[n].get('color', '#34495e') for n in G.nodes()]
        node_sizes = [G.nodes[n].get('size', 25) * 20 for n in G.nodes()]

        # Draw nodes
        nx.draw_networkx_nodes(G, pos,
                               node_color=node_colors,
                               node_size=node_sizes,
                               alpha=0.9,
                               ax=ax)

        # Draw edges
        edge_colors = [G.edges[e].get('color', '#7f8c8d') for e in G.edges()]
        nx.draw_networkx_edges(G, pos,
                               edge_color=edge_colors,
                               arrows=True,
                               arrowsize=15,
                               alpha=0.6,
                               ax=ax)

        # Draw labels
        labels = {n: G.nodes[n].get('label', n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

        # Draw edge labels
        edge_labels = {(e[0], e[1]): G.edges[e].get('label', '') for e in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)

        ax.set_title('Knowledge Graph', fontsize=16, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Graph saved to: {output_path}")

        return fig

    def to_pyvis(self, output_path: str = 'knowledge_graph.html', height: str = '800px', width: str = '100%'):
        """
        Render interactive graph using pyvis.

        Args:
            output_path: Path to save the HTML file
            height: Height of the visualization
            width: Width of the visualization
        """
        try:
            from pyvis.network import Network
        except ImportError:
            raise ImportError("pyvis is required. Install with: pip install pyvis")

        net = Network(height=height, width=width, directed=True, notebook=False)

        # Configure physics
        net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150)

        # Add nodes
        for node_id, node in self.graph.nodes.items():
            net.add_node(node_id,
                         label=node.label,
                         title=f"{node.node_type}: {node.label}",
                         color=node.color,
                         size=node.size)

        # Add edges
        for edge in self.graph.edges:
            net.add_edge(edge.source, edge.target,
                         title=edge.label,
                         label=edge.label,
                         color=edge.color)

        # Save to HTML
        net.save_graph(output_path)
        print(f"Interactive graph saved to: {output_path}")

        return output_path

    def to_interactive_html(self, output_path: str = 'knowledge_graph.html'):
        """
        Generate an advanced interactive HTML visualization with filtering,
        search, and flow visualization capabilities.

        Args:
            output_path: Path to save the HTML file
        """
        # Collect node types and edge types for filters
        node_types = set()
        edge_types = set()
        for node in self.graph.nodes.values():
            node_types.add(node.node_type)
        for edge in self.graph.edges:
            edge_types.add(edge.label)

        # Prepare data for JavaScript
        graph_data = self.graph.to_json()

        # Color maps
        node_color_map = {
            'class': '#e74c3c',
            'function': '#3498db',
            'method': '#9b59b6',
            'variable': '#2ecc71',
            'import': '#f39c12',
            'module': '#1abc9c',
            'entry_point': '#00ff00',   # Bright green for START
            'exit_point': '#ff0000',     # Bright red for END
            'PERSON': '#e74c3c',
            'ORG': '#3498db',
            'GPE': '#2ecc71',
            'CONCEPT': '#9b59b6',
            'NOUN': '#f39c12',
            'TECHNICAL': '#1abc9c',
            'STRING': '#95a5a6',
            'default': '#34495e'
        }

        edge_color_map = {
            'inherits': '#e74c3c',
            'extends': '#e74c3c',
            'implements': '#c0392b',
            'imports': '#f39c12',
            'calls': '#3498db',
            'uses': '#2ecc71',
            'contains': '#9b59b6',
            'is_a': '#1abc9c',
            'has': '#27ae60',
            'depends_on': '#e67e22',
            'exports': '#16a085',
            'starts_at': '#00ff00',      # Green for flow start
            'executes': '#00ffff',       # Cyan for execution
            'ends_at': '#ff0000',        # Red for flow end
            'default': '#7f8c8d'
        }

        html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph - Interactive Viewer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/vis-network.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            display: flex;
            height: 100vh;
        }}

        /* Sidebar */
        .sidebar {{
            width: 320px;
            background: #16213e;
            padding: 20px;
            overflow-y: auto;
            border-right: 2px solid #0f3460;
        }}
        .sidebar h2 {{
            color: #e94560;
            margin-bottom: 20px;
            font-size: 1.4em;
            border-bottom: 2px solid #0f3460;
            padding-bottom: 10px;
        }}
        .sidebar h3 {{
            color: #00d9ff;
            margin: 15px 0 10px 0;
            font-size: 1.1em;
        }}

        /* Search */
        .search-box {{
            width: 100%;
            padding: 12px;
            border: 2px solid #0f3460;
            border-radius: 8px;
            background: #1a1a2e;
            color: #fff;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .search-box:focus {{
            outline: none;
            border-color: #e94560;
        }}

        /* Filter sections */
        .filter-section {{
            margin-bottom: 20px;
            background: #1a1a2e;
            padding: 15px;
            border-radius: 8px;
        }}
        .filter-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            cursor: pointer;
        }}
        .filter-item input {{
            margin-right: 10px;
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        .filter-item label {{
            cursor: pointer;
            display: flex;
            align-items: center;
            flex: 1;
        }}
        .color-dot {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 8px;
            display: inline-block;
        }}
        .count-badge {{
            background: #0f3460;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: auto;
        }}

        /* Buttons */
        .btn {{
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: #e94560;
            color: white;
        }}
        .btn-primary:hover {{
            background: #ff6b6b;
        }}
        .btn-secondary {{
            background: #0f3460;
            color: white;
        }}
        .btn-secondary:hover {{
            background: #1a4a7a;
        }}
        .btn-group {{
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }}

        /* Stats */
        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #00d9ff;
        }}
        .stat-label {{
            font-size: 12px;
            color: #aaa;
        }}

        /* Graph container */
        .graph-container {{
            flex: 1;
            position: relative;
        }}
        #graph {{
            width: 100%;
            height: 100%;
            background: #1a1a2e;
        }}

        /* Info panel */
        .info-panel {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(22, 33, 62, 0.95);
            padding: 20px;
            border-radius: 10px;
            max-width: 350px;
            display: none;
            border: 2px solid #0f3460;
        }}
        .info-panel.active {{
            display: block;
        }}
        .info-panel h4 {{
            color: #e94560;
            margin-bottom: 10px;
        }}
        .info-panel .close-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            color: #aaa;
            font-size: 20px;
            cursor: pointer;
        }}
        .info-row {{
            margin: 8px 0;
            display: flex;
        }}
        .info-label {{
            color: #00d9ff;
            width: 100px;
        }}
        .info-value {{
            color: #fff;
        }}

        /* Legend */
        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(22, 33, 62, 0.95);
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #0f3460;
        }}
        .legend h4 {{
            color: #e94560;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-line {{
            width: 30px;
            height: 3px;
            margin-right: 8px;
            border-radius: 2px;
        }}

        /* Layout buttons */
        .layout-buttons {{
            position: absolute;
            top: 20px;
            left: 340px;
            display: flex;
            gap: 10px;
        }}

        /* Flow view */
        .flow-indicator {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(22, 33, 62, 0.95);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 12px;
            color: #00d9ff;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Knowledge Graph</h2>

        <input type="text" class="search-box" id="searchBox" placeholder="Suchen... (Name oder Typ)">

        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="nodeCount">0</div>
                <div class="stat-label">Knoten</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="edgeCount">0</div>
                <div class="stat-label">Beziehungen</div>
            </div>
        </div>

        <div class="btn-group">
            <button class="btn btn-primary" onclick="selectAll()">Alle auswählen</button>
            <button class="btn btn-secondary" onclick="deselectAll()">Alle abwählen</button>
            <button class="btn btn-secondary" onclick="resetView()">Ansicht zurücksetzen</button>
        </div>

        <h3>Knoten-Typen filtern</h3>
        <div class="filter-section" id="nodeFilters"></div>

        <h3>Beziehungen filtern</h3>
        <div class="filter-section" id="edgeFilters"></div>

        <h3>Ansicht</h3>
        <div class="btn-group">
            <button class="btn btn-secondary" onclick="setLayout('hierarchical')">Hierarchisch</button>
            <button class="btn btn-secondary" onclick="setLayout('flow')">Ablauf</button>
            <button class="btn btn-secondary" onclick="setLayout('circular')">Kreisförmig</button>
            <button class="btn btn-secondary" onclick="setLayout('free')">Frei</button>
        </div>

        <h3>Fokus</h3>
        <div class="btn-group">
            <button class="btn btn-secondary" onclick="focusOnClasses()">Nur Klassen</button>
            <button class="btn btn-secondary" onclick="focusOnFlow()">Nur Ablauf</button>
            <button class="btn btn-secondary" onclick="focusOnInheritance()">Vererbung</button>
        </div>
    </div>

    <div class="graph-container">
        <div id="graph"></div>

        <div class="info-panel" id="infoPanel">
            <button class="close-btn" onclick="closeInfoPanel()">&times;</button>
            <h4 id="infoTitle">Details</h4>
            <div id="infoContent"></div>
        </div>

        <div class="legend" id="legend">
            <h4>Legende - Beziehungen</h4>
            <div id="legendContent"></div>
        </div>

        <div class="flow-indicator" id="flowIndicator">
            Klicken Sie auf einen Knoten für Details
        </div>
    </div>

    <script>
        // Graph data
        const graphData = {json.dumps(graph_data)};
        const nodeColorMap = {json.dumps(node_color_map)};
        const edgeColorMap = {json.dumps(edge_color_map)};

        // State
        let network = null;
        let allNodes = [];
        let allEdges = [];
        let activeNodeTypes = new Set();
        let activeEdgeTypes = new Set();

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            initializeGraph();
            createFilters();
            createLegend();
            updateStats();
        }});

        function initializeGraph() {{
            // Prepare nodes
            allNodes = graphData.nodes.map(node => ({{
                id: node.id,
                label: node.label,
                title: `<b>${{node.type}}</b><br>${{node.label}}${{node.docstring ? '<br><i>' + node.docstring + '</i>' : ''}}${{node.line_number ? '<br>Zeile: ' + node.line_number : ''}}`,
                color: {{
                    background: nodeColorMap[node.type] || nodeColorMap['default'],
                    border: '#fff',
                    highlight: {{ background: '#fff', border: nodeColorMap[node.type] || nodeColorMap['default'] }}
                }},
                font: {{ color: '#fff', size: 14 }},
                shape: getNodeShape(node.type),
                size: 25,
                nodeType: node.type,
                file_path: node.file_path,
                line_number: node.line_number,
                docstring: node.docstring
            }}));

            // Prepare edges
            allEdges = graphData.edges.map((edge, idx) => ({{
                id: idx,
                from: edge.source,
                to: edge.target,
                label: edge.label,
                title: edge.label,
                color: {{
                    color: edgeColorMap[edge.label] || edgeColorMap['default'],
                    highlight: '#fff'
                }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }},
                font: {{ color: '#aaa', size: 10, align: 'middle' }},
                smooth: {{ type: 'curvedCW', roundness: 0.2 }},
                edgeType: edge.label
            }}));

            // Collect types
            allNodes.forEach(n => activeNodeTypes.add(n.nodeType));
            allEdges.forEach(e => activeEdgeTypes.add(e.edgeType));

            // Create network
            const container = document.getElementById('graph');
            const data = {{
                nodes: new vis.DataSet(allNodes),
                edges: new vis.DataSet(allEdges)
            }};

            const options = {{
                physics: {{
                    enabled: true,
                    barnesHut: {{
                        gravitationalConstant: -3000,
                        centralGravity: 0.3,
                        springLength: 150,
                        springConstant: 0.04
                    }},
                    stabilization: {{ iterations: 100 }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true
                }},
                nodes: {{
                    borderWidth: 2,
                    shadow: true
                }},
                edges: {{
                    width: 2,
                    shadow: true
                }}
            }};

            network = new vis.Network(container, data, options);

            // Event handlers
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    showNodeInfo(params.nodes[0]);
                }}
            }});

            network.on('hoverNode', function(params) {{
                document.getElementById('flowIndicator').textContent =
                    'Knoten: ' + params.node;
            }});
        }}

        function getNodeShape(type) {{
            const shapes = {{
                'class': 'box',
                'function': 'ellipse',
                'method': 'diamond',
                'variable': 'dot',
                'import': 'triangle',
                'module': 'hexagon',
                'entry_point': 'star',
                'exit_point': 'star',
                'default': 'box'
            }};
            return shapes[type] || shapes['default'];
        }}

        function createFilters() {{
            // Node type filters
            const nodeFilterContainer = document.getElementById('nodeFilters');
            const nodeTypeCounts = {{}};
            allNodes.forEach(n => {{
                nodeTypeCounts[n.nodeType] = (nodeTypeCounts[n.nodeType] || 0) + 1;
            }});

            Object.keys(nodeTypeCounts).sort().forEach(type => {{
                const color = nodeColorMap[type] || nodeColorMap['default'];
                nodeFilterContainer.innerHTML += `
                    <div class="filter-item">
                        <input type="checkbox" id="node_${{type}}" checked onchange="filterGraph()">
                        <label for="node_${{type}}">
                            <span class="color-dot" style="background: ${{color}}"></span>
                            ${{type}}
                            <span class="count-badge">${{nodeTypeCounts[type]}}</span>
                        </label>
                    </div>
                `;
            }});

            // Edge type filters
            const edgeFilterContainer = document.getElementById('edgeFilters');
            const edgeTypeCounts = {{}};
            allEdges.forEach(e => {{
                edgeTypeCounts[e.edgeType] = (edgeTypeCounts[e.edgeType] || 0) + 1;
            }});

            Object.keys(edgeTypeCounts).sort().forEach(type => {{
                const color = edgeColorMap[type] || edgeColorMap['default'];
                edgeFilterContainer.innerHTML += `
                    <div class="filter-item">
                        <input type="checkbox" id="edge_${{type}}" checked onchange="filterGraph()">
                        <label for="edge_${{type}}">
                            <span class="color-dot" style="background: ${{color}}"></span>
                            ${{type}}
                            <span class="count-badge">${{edgeTypeCounts[type]}}</span>
                        </label>
                    </div>
                `;
            }});
        }}

        function createLegend() {{
            const legendContent = document.getElementById('legendContent');
            const edgeTypes = [...new Set(allEdges.map(e => e.edgeType))];

            edgeTypes.forEach(type => {{
                const color = edgeColorMap[type] || edgeColorMap['default'];
                legendContent.innerHTML += `
                    <div class="legend-item">
                        <div class="legend-line" style="background: ${{color}}"></div>
                        ${{type}}
                    </div>
                `;
            }});
        }}

        function filterGraph() {{
            // Get active node types
            activeNodeTypes = new Set();
            allNodes.forEach(n => {{
                const checkbox = document.getElementById('node_' + n.nodeType);
                if (checkbox && checkbox.checked) {{
                    activeNodeTypes.add(n.nodeType);
                }}
            }});

            // Get active edge types
            activeEdgeTypes = new Set();
            allEdges.forEach(e => {{
                const checkbox = document.getElementById('edge_' + e.edgeType);
                if (checkbox && checkbox.checked) {{
                    activeEdgeTypes.add(e.edgeType);
                }}
            }});

            // Filter nodes
            const visibleNodes = allNodes.filter(n => activeNodeTypes.has(n.nodeType));
            const visibleNodeIds = new Set(visibleNodes.map(n => n.id));

            // Filter edges (both nodes must be visible and edge type must be active)
            const visibleEdges = allEdges.filter(e =>
                visibleNodeIds.has(e.from) &&
                visibleNodeIds.has(e.to) &&
                activeEdgeTypes.has(e.edgeType)
            );

            // Update network
            network.setData({{
                nodes: new vis.DataSet(visibleNodes),
                edges: new vis.DataSet(visibleEdges)
            }});

            updateStats(visibleNodes.length, visibleEdges.length);
        }}

        function updateStats(nodes, edges) {{
            document.getElementById('nodeCount').textContent = nodes !== undefined ? nodes : allNodes.length;
            document.getElementById('edgeCount').textContent = edges !== undefined ? edges : allEdges.length;
        }}

        function selectAll() {{
            document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => cb.checked = true);
            filterGraph();
        }}

        function deselectAll() {{
            document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => cb.checked = false);
            filterGraph();
        }}

        function resetView() {{
            selectAll();
            network.fit();
            setLayout('free');
        }}

        function setLayout(type) {{
            let options = {{}};

            switch(type) {{
                case 'hierarchical':
                    options = {{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'UD',
                                sortMethod: 'directed',
                                levelSeparation: 100,
                                nodeSpacing: 150
                            }}
                        }},
                        physics: {{ enabled: false }}
                    }};
                    break;
                case 'flow':
                    options = {{
                        layout: {{
                            hierarchical: {{
                                enabled: true,
                                direction: 'LR',
                                sortMethod: 'directed',
                                levelSeparation: 200,
                                nodeSpacing: 100
                            }}
                        }},
                        physics: {{ enabled: false }}
                    }};
                    break;
                case 'circular':
                    options = {{
                        layout: {{
                            hierarchical: {{ enabled: false }},
                            improvedLayout: true
                        }},
                        physics: {{
                            enabled: true,
                            solver: 'forceAtlas2Based',
                            forceAtlas2Based: {{
                                gravitationalConstant: -50,
                                centralGravity: 0.01,
                                springLength: 200
                            }}
                        }}
                    }};
                    break;
                default: // free
                    options = {{
                        layout: {{ hierarchical: {{ enabled: false }} }},
                        physics: {{
                            enabled: true,
                            barnesHut: {{
                                gravitationalConstant: -3000,
                                centralGravity: 0.3,
                                springLength: 150
                            }}
                        }}
                    }};
            }}

            network.setOptions(options);
            document.getElementById('flowIndicator').textContent = 'Layout: ' + type;
        }}

        function focusOnClasses() {{
            document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => cb.checked = false);
            const classCheckbox = document.getElementById('node_class');
            if (classCheckbox) classCheckbox.checked = true;
            const inheritsCheckbox = document.getElementById('edge_inherits');
            if (inheritsCheckbox) inheritsCheckbox.checked = true;
            const extendsCheckbox = document.getElementById('edge_extends');
            if (extendsCheckbox) extendsCheckbox.checked = true;
            filterGraph();
        }}

        function focusOnFlow() {{
            document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => cb.checked = false);
            ['node_entry_point', 'node_exit_point', 'node_class', 'node_function', 'node_method'].forEach(id => {{
                const cb = document.getElementById(id);
                if (cb) cb.checked = true;
            }});
            ['edge_calls', 'edge_contains', 'edge_starts_at', 'edge_executes', 'edge_ends_at'].forEach(id => {{
                const cb = document.getElementById(id);
                if (cb) cb.checked = true;
            }});
            filterGraph();
            setLayout('flow');
        }}

        function focusOnInheritance() {{
            document.querySelectorAll('.filter-section input[type="checkbox"]').forEach(cb => cb.checked = false);
            ['node_class'].forEach(id => {{
                const cb = document.getElementById(id);
                if (cb) cb.checked = true;
            }});
            ['edge_inherits', 'edge_extends', 'edge_implements'].forEach(id => {{
                const cb = document.getElementById(id);
                if (cb) cb.checked = true;
            }});
            filterGraph();
            setLayout('hierarchical');
        }}

        function showNodeInfo(nodeId) {{
            const node = allNodes.find(n => n.id === nodeId);
            if (!node) return;

            const infoPanel = document.getElementById('infoPanel');
            const infoTitle = document.getElementById('infoTitle');
            const infoContent = document.getElementById('infoContent');

            // Find connections
            const incomingEdges = allEdges.filter(e => e.to === nodeId);
            const outgoingEdges = allEdges.filter(e => e.from === nodeId);

            infoTitle.textContent = node.label;
            infoContent.innerHTML = `
                <div class="info-row">
                    <span class="info-label">Typ:</span>
                    <span class="info-value">${{node.nodeType}}</span>
                </div>
                ${{node.file_path ? `
                <div class="info-row">
                    <span class="info-label">Datei:</span>
                    <span class="info-value">${{node.file_path}}</span>
                </div>
                ` : ''}}
                ${{node.line_number ? `
                <div class="info-row">
                    <span class="info-label">Zeile:</span>
                    <span class="info-value">${{node.line_number}}</span>
                </div>
                ` : ''}}
                ${{node.docstring ? `
                <div class="info-row">
                    <span class="info-label">Beschreibung:</span>
                    <span class="info-value">${{node.docstring}}</span>
                </div>
                ` : ''}}
                <div class="info-row">
                    <span class="info-label">Eingehend:</span>
                    <span class="info-value">${{incomingEdges.length}} Verbindungen</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Ausgehend:</span>
                    <span class="info-value">${{outgoingEdges.length}} Verbindungen</span>
                </div>
                ${{incomingEdges.length > 0 ? `
                <h4 style="margin-top: 15px; color: #00d9ff;">Eingehende Beziehungen</h4>
                ${{incomingEdges.map(e => `<div class="info-row"><span class="info-value">${{e.from}} → <b>${{e.label}}</b></span></div>`).join('')}}
                ` : ''}}
                ${{outgoingEdges.length > 0 ? `
                <h4 style="margin-top: 15px; color: #00d9ff;">Ausgehende Beziehungen</h4>
                ${{outgoingEdges.map(e => `<div class="info-row"><span class="info-value"><b>${{e.label}}</b> → ${{e.to}}</span></div>`).join('')}}
                ` : ''}}
            `;

            infoPanel.classList.add('active');

            // Highlight connected nodes
            network.selectNodes([nodeId, ...incomingEdges.map(e => e.from), ...outgoingEdges.map(e => e.to)]);
        }}

        function closeInfoPanel() {{
            document.getElementById('infoPanel').classList.remove('active');
            network.unselectAll();
        }}

        // Search functionality
        document.getElementById('searchBox').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            if (searchTerm.length < 2) {{
                network.unselectAll();
                return;
            }}

            const matchingNodes = allNodes.filter(n =>
                n.label.toLowerCase().includes(searchTerm) ||
                n.nodeType.toLowerCase().includes(searchTerm)
            );

            if (matchingNodes.length > 0) {{
                network.selectNodes(matchingNodes.map(n => n.id));
                network.focus(matchingNodes[0].id, {{ scale: 1.2, animation: true }});
            }}
        }});
    </script>
</body>
</html>
'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Interactive graph with filters saved to: {output_path}")
        return output_path

    def to_json(self, output_path: Optional[str] = None, indent: int = 2) -> str:
        """
        Export graph to JSON format.

        Args:
            output_path: Path to save the JSON file (optional)
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        data = self.graph.to_json()
        json_str = json.dumps(data, indent=indent)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            print(f"Graph JSON saved to: {output_path}")

        return json_str

    def to_dot(self, output_path: Optional[str] = None) -> str:
        """
        Export graph to DOT format (for Graphviz).

        Args:
            output_path: Path to save the DOT file (optional)

        Returns:
            DOT string representation
        """
        lines = ['digraph KnowledgeGraph {']
        lines.append('    rankdir=LR;')
        lines.append('    node [shape=box, style=filled, fontname="Arial"];')
        lines.append('    edge [fontname="Arial", fontsize=10];')
        lines.append('')

        # Add nodes
        for node_id, node in self.graph.nodes.items():
            safe_id = node_id.replace('"', '\\"').replace('.', '_')
            label = node.label.replace('"', '\\"')
            lines.append(f'    "{safe_id}" [label="{label}", fillcolor="{node.color}"];')

        lines.append('')

        # Add edges
        for edge in self.graph.edges:
            source = edge.source.replace('"', '\\"').replace('.', '_')
            target = edge.target.replace('"', '\\"').replace('.', '_')
            label = edge.label.replace('"', '\\"')
            lines.append(f'    "{source}" -> "{target}" [label="{label}", color="{edge.color}"];')

        lines.append('}')

        dot_str = '\n'.join(lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(dot_str)
            print(f"DOT file saved to: {output_path}")

        return dot_str

    def to_mermaid(self, output_path: Optional[str] = None) -> str:
        """
        Export graph to Mermaid diagram format.

        Args:
            output_path: Path to save the Mermaid file (optional)

        Returns:
            Mermaid string representation
        """
        lines = ['```mermaid', 'graph LR']

        # Add nodes with styling
        node_styles = {}
        for node_id, node in self.graph.nodes.items():
            safe_id = node_id.replace(' ', '_').replace('.', '_').replace('-', '_')
            label = node.label.replace('"', "'")
            lines.append(f'    {safe_id}["{label}"]')
            node_styles[node.node_type] = node.color

        lines.append('')

        # Add edges
        for edge in self.graph.edges:
            source = edge.source.replace(' ', '_').replace('.', '_').replace('-', '_')
            target = edge.target.replace(' ', '_').replace('.', '_').replace('-', '_')
            label = edge.label
            lines.append(f'    {source} -->|{label}| {target}')

        lines.append('```')

        mermaid_str = '\n'.join(lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(mermaid_str)
            print(f"Mermaid diagram saved to: {output_path}")

        return mermaid_str

    def print_summary(self):
        """Print a summary of the graph."""
        print("\n" + "=" * 50)
        print("KNOWLEDGE GRAPH SUMMARY")
        print("=" * 50)
        print(f"Total Nodes: {len(self.graph.nodes)}")
        print(f"Total Edges: {len(self.graph.edges)}")

        # Count by type
        node_types = {}
        for node in self.graph.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1

        print("\nNode Types:")
        for ntype, count in sorted(node_types.items(), key=lambda x: -x[1]):
            print(f"  - {ntype}: {count}")

        edge_types = {}
        for edge in self.graph.edges:
            edge_types[edge.label] = edge_types.get(edge.label, 0) + 1

        print("\nRelationship Types:")
        for etype, count in sorted(edge_types.items(), key=lambda x: -x[1]):
            print(f"  - {etype}: {count}")

        print("=" * 50 + "\n")


def main():
    """Test the visualizer."""
    # Create a sample knowledge graph
    graph = KnowledgeGraph()

    # Add nodes
    graph.add_node(Node(id='Python', label='Python', node_type='class'))
    graph.add_node(Node(id='Django', label='Django', node_type='class'))
    graph.add_node(Node(id='Flask', label='Flask', node_type='class'))
    graph.add_node(Node(id='WebFramework', label='Web Framework', node_type='CONCEPT'))

    # Add edges
    graph.add_edge(Edge(source='Django', target='Python', label='uses'))
    graph.add_edge(Edge(source='Flask', target='Python', label='uses'))
    graph.add_edge(Edge(source='Django', target='WebFramework', label='is_a'))
    graph.add_edge(Edge(source='Flask', target='WebFramework', label='is_a'))

    # Visualize
    visualizer = GraphVisualizer(graph)
    visualizer.print_summary()

    # Export to different formats
    print(visualizer.to_mermaid())


if __name__ == "__main__":
    main()
