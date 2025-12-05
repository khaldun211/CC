# Knowledge Graph Generator

A Python tool that generates knowledge graphs from text documents or source code. It extracts entities, relationships, and visualizes them as interactive graphs.

## Features

- **Text Analysis**: Extract entities and relationships from natural language text
- **Code Analysis**: Parse Python, JavaScript, Java, C++, and Go source code
- **Multiple Output Formats**: HTML (interactive), PNG, JSON, DOT, Mermaid
- **Visualization**: Interactive graph visualization using pyvis
- **Extensible**: Easy to add new parsers and visualization formats

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For advanced NLP features (optional)
pip install spacy
python -m spacy download en_core_web_sm
```

## Quick Start

### Generate from Code

```bash
# Analyze a Python file
python knowledge_graph_generator.py --input examples/sample_code.py --type code

# Analyze a directory
python knowledge_graph_generator.py --input ./src --type code --format html
```

### Generate from Text

```bash
# Analyze a text file
python knowledge_graph_generator.py --input examples/sample_text.txt --type text

# Analyze inline text
python knowledge_graph_generator.py --input "Python is a language. Django uses Python." --type text
```

### Output Formats

```bash
# Interactive HTML (default)
python knowledge_graph_generator.py --input code.py --format html --output graph.html

# Static PNG image
python knowledge_graph_generator.py --input code.py --format png --output graph.png

# JSON for further processing
python knowledge_graph_generator.py --input code.py --format json --output graph.json

# DOT format for Graphviz
python knowledge_graph_generator.py --input code.py --format dot --output graph.dot

# Mermaid diagram (for Markdown)
python knowledge_graph_generator.py --input code.py --format mermaid --output graph.md
```

## Usage as Library

```python
from knowledge_graph_generator import KnowledgeGraphGenerator

# Initialize
generator = KnowledgeGraphGenerator()

# Process text
text = """
Python is a programming language.
Django is a web framework.
Django uses Python.
"""
graph = generator.process_text(text)

# Process code
code = open('mycode.py').read()
graph = generator.process_code(code, 'mycode.py')

# Process files
graph = generator.process_file('mycode.py')

# Process directory
graph = generator.process_directory('./src', extensions=['.py', '.js'])

# Visualize
generator.visualize('output.html', format='html')
generator.get_summary()
```

## Extracted Relationships

### From Text
- `is_a` - Classification relationships
- `has` - Possession relationships
- `uses` - Usage relationships
- `contains` - Containment relationships
- `depends_on` - Dependency relationships
- `part_of` - Part-whole relationships
- And more...

### From Code
- `inherits` - Class inheritance
- `imports` - Module imports
- `calls` - Function/method calls
- `contains` - Class contains methods
- `uses` - Variable usage
- `exports` - Module exports

## Command Line Options

```
--input, -i     Input file, directory, or text string (required)
--type, -t      Input type: text, code, or auto (default: auto)
--output, -o    Output file path
--format, -f    Output format: html, png, json, dot, mermaid (default: html)
--extensions    File extensions to process for directories
--use-spacy     Use spaCy for advanced NLP
--summary       Print graph summary
```

## Examples

### Example 1: Analyze Python Project Structure

```bash
python knowledge_graph_generator.py \
    --input /path/to/project \
    --type code \
    --extensions .py \
    --format html \
    --output project_graph.html
```

### Example 2: Create Knowledge Graph from Documentation

```bash
python knowledge_graph_generator.py \
    --input docs/architecture.md \
    --type text \
    --use-spacy \
    --format png \
    --output architecture.png
```

## Project Structure

```
knowledge_graph_generator/
├── __init__.py                 # Package initialization
├── knowledge_graph_generator.py # Main CLI application
├── text_parser.py              # Natural language parser
├── code_parser.py              # Source code parser
├── visualizer.py               # Graph visualization
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── examples/
    ├── sample_code.py          # Sample Python code
    └── sample_text.txt         # Sample text document
```

## Dependencies

- `networkx` - Graph data structures
- `matplotlib` - Static graph visualization
- `pyvis` - Interactive HTML visualization
- `spacy` (optional) - Advanced NLP

## License

MIT License
