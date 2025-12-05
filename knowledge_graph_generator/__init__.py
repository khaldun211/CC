"""
Knowledge Graph Generator
A Python library for generating knowledge graphs from text and source code.
"""

from .text_parser import TextParser, Entity, Relationship
from .code_parser import GenericCodeParser, PythonCodeParser, JavaScriptCodeParser, CodeEntity, CodeRelationship
from .visualizer import KnowledgeGraph, Node, Edge, GraphVisualizer
from .knowledge_graph_generator import KnowledgeGraphGenerator

__version__ = '1.0.0'
__author__ = 'Knowledge Graph Generator'

__all__ = [
    'KnowledgeGraphGenerator',
    'TextParser',
    'Entity',
    'Relationship',
    'GenericCodeParser',
    'PythonCodeParser',
    'JavaScriptCodeParser',
    'CodeEntity',
    'CodeRelationship',
    'KnowledgeGraph',
    'Node',
    'Edge',
    'GraphVisualizer',
]
