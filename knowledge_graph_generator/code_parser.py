"""
Code Parser Module
Parses source code to extract classes, functions, imports, and their relationships.
Supports Python, JavaScript, and basic support for other languages.
"""

import ast
import re
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeEntity:
    """Represents a code entity (class, function, variable, etc.)."""
    name: str
    entity_type: str  # class, function, method, variable, import, module
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    parent: Optional[str] = None
    docstring: Optional[str] = None
    attributes: Dict = field(default_factory=dict)

    def __hash__(self):
        return hash((self.name, self.entity_type, self.parent))

    def __eq__(self, other):
        if isinstance(other, CodeEntity):
            return (self.name == other.name and
                    self.entity_type == other.entity_type and
                    self.parent == other.parent)
        return False


@dataclass
class CodeRelationship:
    """Represents a relationship between code entities."""
    source: str
    target: str
    relation_type: str  # inherits, imports, calls, uses, defines, contains
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    def __hash__(self):
        return hash((self.source, self.target, self.relation_type))

    def __eq__(self, other):
        if isinstance(other, CodeRelationship):
            return (self.source == other.source and
                    self.target == other.target and
                    self.relation_type == other.relation_type)
        return False


class PythonCodeParser:
    """Parses Python source code using AST."""

    def __init__(self):
        self.entities: List[CodeEntity] = []
        self.relationships: List[CodeRelationship] = []
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.file_path: Optional[str] = None

    def parse(self, code: str, file_path: Optional[str] = None) -> Tuple[List[CodeEntity], List[CodeRelationship]]:
        """
        Parse Python code and extract entities and relationships.

        Args:
            code: Python source code string
            file_path: Optional path to the source file

        Returns:
            Tuple of (entities, relationships)
        """
        self.entities = []
        self.relationships = []
        self.file_path = file_path

        try:
            tree = ast.parse(code)
            self._visit(tree)
        except SyntaxError as e:
            print(f"Syntax error parsing Python code: {e}")

        return self.entities, self.relationships

    def _visit(self, node: ast.AST, parent: Optional[str] = None):
        """Visit AST nodes recursively."""
        if isinstance(node, ast.Module):
            for child in ast.iter_child_nodes(node):
                self._visit(child)

        elif isinstance(node, ast.ClassDef):
            self._handle_class(node, parent)

        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            self._handle_function(node, parent)

        elif isinstance(node, ast.Import):
            self._handle_import(node)

        elif isinstance(node, ast.ImportFrom):
            self._handle_import_from(node)

        elif isinstance(node, ast.Assign):
            self._handle_assignment(node, parent)

        elif isinstance(node, ast.Call):
            self._handle_call(node, parent)

        else:
            for child in ast.iter_child_nodes(node):
                self._visit(child, parent)

    def _handle_class(self, node: ast.ClassDef, parent: Optional[str]):
        """Handle class definition."""
        class_entity = CodeEntity(
            name=node.name,
            entity_type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            parent=parent,
            docstring=ast.get_docstring(node)
        )
        self.entities.append(class_entity)

        # Handle inheritance
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name:
                rel = CodeRelationship(
                    source=node.name,
                    target=base_name,
                    relation_type='inherits',
                    file_path=self.file_path,
                    line_number=node.lineno
                )
                self.relationships.append(rel)

        # Visit class body
        old_class = self.current_class
        self.current_class = node.name
        for child in node.body:
            self._visit(child, node.name)
        self.current_class = old_class

    def _handle_function(self, node, parent: Optional[str]):
        """Handle function/method definition."""
        entity_type = 'method' if self.current_class else 'function'
        func_entity = CodeEntity(
            name=node.name,
            entity_type=entity_type,
            file_path=self.file_path,
            line_number=node.lineno,
            parent=parent or self.current_class,
            docstring=ast.get_docstring(node)
        )
        self.entities.append(func_entity)

        # Add contains relationship
        if parent:
            rel = CodeRelationship(
                source=parent,
                target=node.name,
                relation_type='contains',
                file_path=self.file_path,
                line_number=node.lineno
            )
            self.relationships.append(rel)

        # Visit function body
        old_function = self.current_function
        self.current_function = node.name
        for child in node.body:
            self._visit(child, node.name)
        self.current_function = old_function

    def _handle_import(self, node: ast.Import):
        """Handle import statement."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            import_entity = CodeEntity(
                name=name,
                entity_type='import',
                file_path=self.file_path,
                line_number=node.lineno,
                attributes={'module': alias.name}
            )
            self.entities.append(import_entity)

            # Add import relationship
            rel = CodeRelationship(
                source='module',
                target=alias.name,
                relation_type='imports',
                file_path=self.file_path,
                line_number=node.lineno
            )
            self.relationships.append(rel)

    def _handle_import_from(self, node: ast.ImportFrom):
        """Handle from ... import ... statement."""
        module = node.module or ''
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            import_entity = CodeEntity(
                name=name,
                entity_type='import',
                file_path=self.file_path,
                line_number=node.lineno,
                attributes={'module': module, 'original_name': alias.name}
            )
            self.entities.append(import_entity)

            rel = CodeRelationship(
                source='module',
                target=f"{module}.{alias.name}" if module else alias.name,
                relation_type='imports',
                file_path=self.file_path,
                line_number=node.lineno
            )
            self.relationships.append(rel)

    def _handle_assignment(self, node: ast.Assign, parent: Optional[str]):
        """Handle variable assignment."""
        for target in node.targets:
            name = self._get_name(target)
            if name and not name.startswith('_'):
                var_entity = CodeEntity(
                    name=name,
                    entity_type='variable',
                    file_path=self.file_path,
                    line_number=node.lineno,
                    parent=parent
                )
                self.entities.append(var_entity)

    def _handle_call(self, node: ast.Call, parent: Optional[str]):
        """Handle function/method calls."""
        func_name = self._get_name(node.func)
        if func_name and parent:
            rel = CodeRelationship(
                source=parent,
                target=func_name,
                relation_type='calls',
                file_path=self.file_path,
                line_number=node.lineno if hasattr(node, 'lineno') else None
            )
            self.relationships.append(rel)

        # Visit call arguments
        for child in ast.iter_child_nodes(node):
            self._visit(child, parent)

    def _get_name(self, node) -> Optional[str]:
        """Get the name from various AST node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_name(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Subscript):
            return self._get_name(node.value)
        return None


class JavaScriptCodeParser:
    """Parses JavaScript source code using regex patterns."""

    def __init__(self):
        self.entities: List[CodeEntity] = []
        self.relationships: List[CodeRelationship] = []

    def parse(self, code: str, file_path: Optional[str] = None) -> Tuple[List[CodeEntity], List[CodeRelationship]]:
        """
        Parse JavaScript code and extract entities and relationships.

        Args:
            code: JavaScript source code string
            file_path: Optional path to the source file

        Returns:
            Tuple of (entities, relationships)
        """
        self.entities = []
        self.relationships = []

        self._extract_classes(code, file_path)
        self._extract_functions(code, file_path)
        self._extract_imports(code, file_path)
        self._extract_exports(code, file_path)
        self._extract_variables(code, file_path)

        return self.entities, self.relationships

    def _extract_classes(self, code: str, file_path: Optional[str]):
        """Extract class definitions."""
        # ES6 class syntax
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            parent_class = match.group(2)
            line_num = code[:match.start()].count('\n') + 1

            self.entities.append(CodeEntity(
                name=class_name,
                entity_type='class',
                file_path=file_path,
                line_number=line_num
            ))

            if parent_class:
                self.relationships.append(CodeRelationship(
                    source=class_name,
                    target=parent_class,
                    relation_type='extends',
                    file_path=file_path,
                    line_number=line_num
                ))

    def _extract_functions(self, code: str, file_path: Optional[str]):
        """Extract function definitions."""
        # Function declarations
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            self.entities.append(CodeEntity(
                name=func_name,
                entity_type='function',
                file_path=file_path,
                line_number=line_num
            ))

        # Arrow functions assigned to const/let/var
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'
        for match in re.finditer(arrow_pattern, code):
            func_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            self.entities.append(CodeEntity(
                name=func_name,
                entity_type='function',
                file_path=file_path,
                line_number=line_num
            ))

    def _extract_imports(self, code: str, file_path: Optional[str]):
        """Extract import statements."""
        # ES6 imports
        import_pattern = r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            named_imports = match.group(1)
            default_import = match.group(2)
            module_path = match.group(3)
            line_num = code[:match.start()].count('\n') + 1

            if named_imports:
                for imp in named_imports.split(','):
                    imp = imp.strip().split(' as ')[0].strip()
                    if imp:
                        self.entities.append(CodeEntity(
                            name=imp,
                            entity_type='import',
                            file_path=file_path,
                            line_number=line_num,
                            attributes={'module': module_path}
                        ))
                        self.relationships.append(CodeRelationship(
                            source='module',
                            target=module_path,
                            relation_type='imports',
                            file_path=file_path,
                            line_number=line_num
                        ))

            if default_import:
                self.entities.append(CodeEntity(
                    name=default_import,
                    entity_type='import',
                    file_path=file_path,
                    line_number=line_num,
                    attributes={'module': module_path, 'default': True}
                ))
                self.relationships.append(CodeRelationship(
                    source='module',
                    target=module_path,
                    relation_type='imports',
                    file_path=file_path,
                    line_number=line_num
                ))

        # CommonJS require
        require_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        for match in re.finditer(require_pattern, code):
            var_name = match.group(1)
            module_path = match.group(2)
            line_num = code[:match.start()].count('\n') + 1

            self.entities.append(CodeEntity(
                name=var_name,
                entity_type='import',
                file_path=file_path,
                line_number=line_num,
                attributes={'module': module_path}
            ))
            self.relationships.append(CodeRelationship(
                source='module',
                target=module_path,
                relation_type='imports',
                file_path=file_path,
                line_number=line_num
            ))

    def _extract_exports(self, code: str, file_path: Optional[str]):
        """Extract export statements."""
        # Named exports
        export_pattern = r'export\s+(?:const|let|var|function|class)\s+(\w+)'
        for match in re.finditer(export_pattern, code):
            name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            self.relationships.append(CodeRelationship(
                source='module',
                target=name,
                relation_type='exports',
                file_path=file_path,
                line_number=line_num
            ))

        # Default export
        default_export_pattern = r'export\s+default\s+(\w+)'
        for match in re.finditer(default_export_pattern, code):
            name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            self.relationships.append(CodeRelationship(
                source='module',
                target=name,
                relation_type='exports_default',
                file_path=file_path,
                line_number=line_num
            ))

    def _extract_variables(self, code: str, file_path: Optional[str]):
        """Extract variable declarations."""
        var_pattern = r'(?:const|let|var)\s+(\w+)\s*='
        for match in re.finditer(var_pattern, code):
            var_name = match.group(1)
            # Skip if it's likely a function (already captured)
            if var_name.startswith('_'):
                continue
            line_num = code[:match.start()].count('\n') + 1

            self.entities.append(CodeEntity(
                name=var_name,
                entity_type='variable',
                file_path=file_path,
                line_number=line_num
            ))


class GenericCodeParser:
    """Generic code parser for multiple languages using pattern matching."""

    LANGUAGE_PATTERNS = {
        'python': {
            'class': r'class\s+(\w+)',
            'function': r'def\s+(\w+)',
            'import': r'import\s+(\w+)|from\s+(\w+)\s+import',
        },
        'javascript': {
            'class': r'class\s+(\w+)',
            'function': r'function\s+(\w+)|(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
            'import': r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\)',
        },
        'java': {
            'class': r'(?:public|private|protected)?\s*class\s+(\w+)',
            'function': r'(?:public|private|protected)?\s*(?:static\s+)?\w+\s+(\w+)\s*\(',
            'import': r'import\s+([\w.]+)',
        },
        'cpp': {
            'class': r'class\s+(\w+)',
            'function': r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{',
            'import': r'#include\s*[<"]([^>"]+)[>"]',
        },
        'go': {
            'struct': r'type\s+(\w+)\s+struct',
            'function': r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(',
            'import': r'import\s+["\']([^"\']+)["\']',
        },
    }

    def __init__(self, language: str = 'auto'):
        self.language = language

    def detect_language(self, code: str, file_path: Optional[str] = None) -> str:
        """Detect the programming language from code or file extension."""
        if file_path:
            ext = Path(file_path).suffix.lower()
            ext_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'javascript',
                '.jsx': 'javascript',
                '.tsx': 'javascript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.c': 'cpp',
                '.h': 'cpp',
                '.go': 'go',
            }
            if ext in ext_map:
                return ext_map[ext]

        # Heuristic detection based on code content
        if 'def ' in code and ':' in code:
            return 'python'
        elif 'function ' in code or '=>' in code:
            return 'javascript'
        elif 'public class' in code or 'private class' in code:
            return 'java'
        elif '#include' in code:
            return 'cpp'
        elif 'func ' in code and 'package ' in code:
            return 'go'

        return 'generic'

    def parse(self, code: str, file_path: Optional[str] = None) -> Tuple[List[CodeEntity], List[CodeRelationship]]:
        """
        Parse code and extract entities and relationships.

        Args:
            code: Source code string
            file_path: Optional path to the source file

        Returns:
            Tuple of (entities, relationships)
        """
        language = self.language
        if language == 'auto':
            language = self.detect_language(code, file_path)

        # Use specialized parser for Python
        if language == 'python':
            parser = PythonCodeParser()
            return parser.parse(code, file_path)

        # Use specialized parser for JavaScript
        if language == 'javascript':
            parser = JavaScriptCodeParser()
            return parser.parse(code, file_path)

        # Use generic pattern matching for other languages
        return self._parse_generic(code, file_path, language)

    def _parse_generic(self, code: str, file_path: Optional[str], language: str) -> Tuple[List[CodeEntity], List[CodeRelationship]]:
        """Parse code using generic pattern matching."""
        entities = []
        relationships = []

        patterns = self.LANGUAGE_PATTERNS.get(language, self.LANGUAGE_PATTERNS.get('generic', {}))

        for entity_type, pattern in patterns.items():
            for match in re.finditer(pattern, code):
                # Get the first non-None group
                name = next((g for g in match.groups() if g), None)
                if name:
                    line_num = code[:match.start()].count('\n') + 1
                    entities.append(CodeEntity(
                        name=name,
                        entity_type=entity_type,
                        file_path=file_path,
                        line_number=line_num
                    ))

        return entities, relationships


def main():
    """Test the code parser."""
    python_code = '''
import os
from typing import List, Dict

class Animal:
    """Base class for animals."""

    def __init__(self, name: str):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    """A dog that can bark."""

    def speak(self):
        return "Woof!"

    def fetch(self, item):
        print(f"Fetching {item}")

def create_animal(animal_type: str) -> Animal:
    """Factory function for creating animals."""
    if animal_type == "dog":
        return Dog("Buddy")
    return Animal("Generic")

my_dog = create_animal("dog")
'''

    parser = GenericCodeParser(language='python')
    entities, relationships = parser.parse(python_code)

    print("Extracted Code Entities:")
    for entity in entities:
        parent_str = f" (in {entity.parent})" if entity.parent else ""
        print(f"  - [{entity.entity_type}] {entity.name}{parent_str} @ line {entity.line_number}")

    print("\nExtracted Code Relationships:")
    for rel in relationships:
        print(f"  - {rel.source} --[{rel.relation_type}]--> {rel.target}")


if __name__ == "__main__":
    main()
