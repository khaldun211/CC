#!/usr/bin/env python3
"""
Knowledge Graph Generator
A tool to generate knowledge graphs from text or source code.

Usage:
    python knowledge_graph_generator.py --input <file_or_text> [options]

Examples:
    # Generate from a Python file
    python knowledge_graph_generator.py --input mycode.py --type code --output graph.html

    # Generate from text
    python knowledge_graph_generator.py --input "Python is a language. Django uses Python." --type text

    # Generate from multiple files
    python knowledge_graph_generator.py --input src/ --type code --format json
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from text_parser import TextParser, Entity, Relationship
from code_parser import GenericCodeParser, CodeEntity, CodeRelationship
from visualizer import KnowledgeGraph, Node, Edge, GraphVisualizer


class KnowledgeGraphGenerator:
    """
    Main class for generating knowledge graphs from text or code.
    """

    def __init__(self, use_spacy: bool = False):
        """
        Initialize the generator.

        Args:
            use_spacy: Whether to use spaCy for NLP (requires model download)
        """
        self.text_parser = TextParser(use_spacy=use_spacy)
        self.code_parser = GenericCodeParser(language='auto')
        self.graph = KnowledgeGraph()

    def process_text(self, text: str) -> KnowledgeGraph:
        """
        Process natural language text and generate a knowledge graph.

        Args:
            text: Input text to analyze

        Returns:
            KnowledgeGraph object
        """
        entities, relationships = self.text_parser.parse(text)

        # Add entities as nodes
        for entity in entities:
            node = Node(
                id=entity.name,
                label=entity.name,
                node_type=entity.entity_type,
                size=20 + (entity.mentions * 5)
            )
            self.graph.add_node(node)

        # Add relationships as edges
        for rel in relationships:
            edge = Edge(
                source=rel.source,
                target=rel.target,
                label=rel.relation_type,
                weight=rel.weight
            )
            self.graph.add_edge(edge)

        return self.graph

    def process_code(self, code: str, file_path: Optional[str] = None) -> KnowledgeGraph:
        """
        Process source code and generate a knowledge graph.

        Args:
            code: Source code to analyze
            file_path: Optional path to the source file

        Returns:
            KnowledgeGraph object
        """
        entities, relationships = self.code_parser.parse(code, file_path)

        # Add entities as nodes
        for entity in entities:
            node_id = f"{entity.parent}.{entity.name}" if entity.parent else entity.name
            node = Node(
                id=node_id,
                label=entity.name,
                node_type=entity.entity_type,
                attributes={
                    'file_path': entity.file_path,
                    'line_number': entity.line_number,
                    'docstring': entity.docstring
                }
            )
            self.graph.add_node(node)

        # Add relationships as edges
        for rel in relationships:
            edge = Edge(
                source=rel.source,
                target=rel.target,
                label=rel.relation_type,
                attributes={
                    'file_path': rel.file_path,
                    'line_number': rel.line_number
                }
            )
            self.graph.add_edge(edge)

        return self.graph

    def process_file(self, file_path: str, input_type: str = 'auto') -> KnowledgeGraph:
        """
        Process a file and generate a knowledge graph.

        Args:
            file_path: Path to the file
            input_type: Type of input ('text', 'code', or 'auto')

        Returns:
            KnowledgeGraph object
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding='utf-8', errors='ignore')

        # Auto-detect type based on file extension
        if input_type == 'auto':
            code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs'}
            if path.suffix.lower() in code_extensions:
                input_type = 'code'
            else:
                input_type = 'text'

        if input_type == 'code':
            return self.process_code(content, file_path)
        else:
            return self.process_text(content)

    def process_directory(self, dir_path: str, extensions: Optional[List[str]] = None) -> KnowledgeGraph:
        """
        Process all files in a directory and generate a combined knowledge graph.

        Args:
            dir_path: Path to the directory
            extensions: List of file extensions to process (e.g., ['.py', '.js'])

        Returns:
            KnowledgeGraph object
        """
        path = Path(dir_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go']

        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                try:
                    print(f"Processing: {file_path}")
                    self.process_file(str(file_path), 'code')
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        return self.graph

    def visualize(self, output_path: Optional[str] = None, format: str = 'html') -> str:
        """
        Visualize the knowledge graph.

        Args:
            output_path: Path to save the visualization
            format: Output format ('html', 'png', 'json', 'dot', 'mermaid')

        Returns:
            Path to the output file or visualization string
        """
        visualizer = GraphVisualizer(self.graph)

        if output_path is None:
            output_path = f'knowledge_graph.{format}'

        if format == 'html':
            return visualizer.to_pyvis(output_path)
        elif format == 'png':
            fig = visualizer.to_matplotlib(output_path)
            return output_path
        elif format == 'json':
            return visualizer.to_json(output_path)
        elif format == 'dot':
            return visualizer.to_dot(output_path)
        elif format == 'mermaid':
            return visualizer.to_mermaid(output_path)
        else:
            raise ValueError(f"Unknown format: {format}")

    def get_summary(self) -> str:
        """Get a text summary of the graph."""
        visualizer = GraphVisualizer(self.graph)
        visualizer.print_summary()
        return ""


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate knowledge graphs from text or source code.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from a Python file
  python knowledge_graph_generator.py --input mycode.py --type code

  # Generate from text
  python knowledge_graph_generator.py --input "Python is a language." --type text

  # Generate from a directory
  python knowledge_graph_generator.py --input ./src --type code

  # Output as different formats
  python knowledge_graph_generator.py --input code.py --format json --output graph.json
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input file, directory, or text string'
    )

    parser.add_argument(
        '--type', '-t',
        choices=['text', 'code', 'auto'],
        default='auto',
        help='Type of input (default: auto-detect)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['html', 'png', 'json', 'dot', 'mermaid'],
        default='html',
        help='Output format (default: html)'
    )

    parser.add_argument(
        '--extensions', '-e',
        nargs='+',
        help='File extensions to process (for directories)'
    )

    parser.add_argument(
        '--use-spacy',
        action='store_true',
        help='Use spaCy for advanced NLP (requires spacy and model)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print graph summary'
    )

    args = parser.parse_args()

    # Initialize generator
    generator = KnowledgeGraphGenerator(use_spacy=args.use_spacy)

    # Process input
    input_path = Path(args.input)

    if input_path.is_file():
        print(f"Processing file: {args.input}")
        generator.process_file(args.input, args.type)
    elif input_path.is_dir():
        print(f"Processing directory: {args.input}")
        extensions = args.extensions if args.extensions else None
        generator.process_directory(args.input, extensions)
    else:
        # Treat as raw text input
        print("Processing text input...")
        if args.type == 'code':
            generator.process_code(args.input)
        else:
            generator.process_text(args.input)

    # Print summary if requested
    if args.summary or len(generator.graph.nodes) > 0:
        generator.get_summary()

    # Generate visualization
    if len(generator.graph.nodes) > 0:
        output_path = args.output if args.output else f'knowledge_graph.{args.format}'
        result = generator.visualize(output_path, args.format)
        print(f"\nOutput saved to: {result}")
    else:
        print("No entities found in the input.")


if __name__ == '__main__':
    main()
