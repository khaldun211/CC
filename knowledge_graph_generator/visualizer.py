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
