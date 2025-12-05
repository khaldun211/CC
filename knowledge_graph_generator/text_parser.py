"""
Text Parser Module
Extracts entities and relationships from natural language text.
"""

import re
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass


@dataclass
class Entity:
    """Represents an entity extracted from text."""
    name: str
    entity_type: str
    mentions: int = 1

    def __hash__(self):
        return hash((self.name.lower(), self.entity_type))

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.name.lower() == other.name.lower() and self.entity_type == other.entity_type
        return False


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    source: str
    target: str
    relation_type: str
    weight: float = 1.0

    def __hash__(self):
        return hash((self.source.lower(), self.target.lower(), self.relation_type))

    def __eq__(self, other):
        if isinstance(other, Relationship):
            return (self.source.lower() == other.source.lower() and
                    self.target.lower() == other.target.lower() and
                    self.relation_type == other.relation_type)
        return False


class TextParser:
    """
    Parses text to extract entities and relationships for knowledge graph generation.
    Uses pattern matching and heuristics for entity extraction.
    """

    # Common relationship indicators
    RELATIONSHIP_PATTERNS = [
        (r'(\w+)\s+is\s+a\s+(\w+)', 'is_a'),
        (r'(\w+)\s+are\s+(\w+)', 'is_a'),
        (r'(\w+)\s+has\s+(?:a\s+)?(\w+)', 'has'),
        (r'(\w+)\s+have\s+(?:a\s+)?(\w+)', 'has'),
        (r'(\w+)\s+contains?\s+(\w+)', 'contains'),
        (r'(\w+)\s+includes?\s+(\w+)', 'includes'),
        (r'(\w+)\s+uses?\s+(\w+)', 'uses'),
        (r'(\w+)\s+depends?\s+on\s+(\w+)', 'depends_on'),
        (r'(\w+)\s+creates?\s+(\w+)', 'creates'),
        (r'(\w+)\s+inherits?\s+(?:from\s+)?(\w+)', 'inherits'),
        (r'(\w+)\s+extends?\s+(\w+)', 'extends'),
        (r'(\w+)\s+implements?\s+(\w+)', 'implements'),
        (r'(\w+)\s+connects?\s+(?:to\s+)?(\w+)', 'connects_to'),
        (r'(\w+)\s+relates?\s+(?:to\s+)?(\w+)', 'relates_to'),
        (r'(\w+)\s+belongs?\s+(?:to\s+)?(\w+)', 'belongs_to'),
        (r'(\w+)\s+(?:is\s+)?part\s+of\s+(\w+)', 'part_of'),
        (r'(\w+)\s+(?:is\s+)?composed\s+of\s+(\w+)', 'composed_of'),
        (r'(\w+)\s+interacts?\s+with\s+(\w+)', 'interacts_with'),
        (r'(\w+)\s+calls?\s+(\w+)', 'calls'),
        (r'(\w+)\s+invokes?\s+(\w+)', 'invokes'),
    ]

    # Stop words to filter out
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there'
    }

    def __init__(self, use_spacy: bool = False):
        """
        Initialize the text parser.

        Args:
            use_spacy: If True, use spaCy for advanced NLP (requires model download)
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    print("Downloading spaCy model...")
                    from spacy.cli import download
                    download("en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
            except ImportError:
                print("spaCy not available. Using pattern-based extraction.")
                self.use_spacy = False

    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities from text.

        Args:
            text: Input text to analyze

        Returns:
            List of extracted entities
        """
        if self.use_spacy and self.nlp:
            return self._extract_entities_spacy(text)
        return self._extract_entities_pattern(text)

    def _extract_entities_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy NER."""
        doc = self.nlp(text)
        entities = {}

        # Extract named entities
        for ent in doc.ents:
            entity = Entity(name=ent.text, entity_type=ent.label_)
            if entity in entities:
                entities[entity].mentions += 1
            else:
                entities[entity] = entity

        # Extract noun chunks as concepts
        for chunk in doc.noun_chunks:
            if chunk.root.text.lower() not in self.STOP_WORDS:
                entity = Entity(name=chunk.root.text, entity_type='CONCEPT')
                if entity in entities:
                    entities[entity].mentions += 1
                else:
                    entities[entity] = entity

        return list(entities.values())

    def _extract_entities_pattern(self, text: str) -> List[Entity]:
        """Extract entities using pattern matching."""
        entities = {}

        # Extract capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        for word in capitalized:
            if word.lower() not in self.STOP_WORDS:
                entity = Entity(name=word, entity_type='NOUN')
                if entity in entities:
                    entities[entity].mentions += 1
                else:
                    entities[entity] = entity

        # Extract technical terms (CamelCase, snake_case, etc.)
        camel_case = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', text)
        for word in camel_case:
            entity = Entity(name=word, entity_type='TECHNICAL')
            if entity in entities:
                entities[entity].mentions += 1
            else:
                entities[entity] = entity

        snake_case = re.findall(r'\b([a-z]+(?:_[a-z]+)+)\b', text)
        for word in snake_case:
            entity = Entity(name=word, entity_type='TECHNICAL')
            if entity in entities:
                entities[entity].mentions += 1
            else:
                entities[entity] = entity

        # Extract quoted strings
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        for word in quoted:
            if len(word) > 2 and word.lower() not in self.STOP_WORDS:
                entity = Entity(name=word, entity_type='STRING')
                if entity in entities:
                    entities[entity].mentions += 1
                else:
                    entities[entity] = entity

        # Extract words after "the" (often important nouns)
        the_nouns = re.findall(r'\bthe\s+(\w+)', text, re.IGNORECASE)
        for word in the_nouns:
            if word.lower() not in self.STOP_WORDS and len(word) > 2:
                entity = Entity(name=word, entity_type='NOUN')
                if entity in entities:
                    entities[entity].mentions += 1
                else:
                    entities[entity] = entity

        return list(entities.values())

    def extract_relationships(self, text: str) -> List[Relationship]:
        """
        Extract relationships between entities from text.

        Args:
            text: Input text to analyze

        Returns:
            List of extracted relationships
        """
        if self.use_spacy and self.nlp:
            return self._extract_relationships_spacy(text)
        return self._extract_relationships_pattern(text)

    def _extract_relationships_spacy(self, text: str) -> List[Relationship]:
        """Extract relationships using spaCy dependency parsing."""
        doc = self.nlp(text)
        relationships = set()

        for token in doc:
            # Subject-verb-object patterns
            if token.dep_ == 'nsubj' and token.head.pos_ == 'VERB':
                verb = token.head
                for child in verb.children:
                    if child.dep_ in ('dobj', 'pobj', 'attr'):
                        rel = Relationship(
                            source=token.text,
                            target=child.text,
                            relation_type=verb.lemma_
                        )
                        relationships.add(rel)

        # Also use pattern matching for additional relationships
        pattern_rels = self._extract_relationships_pattern(text)
        relationships.update(pattern_rels)

        return list(relationships)

    def _extract_relationships_pattern(self, text: str) -> List[Relationship]:
        """Extract relationships using pattern matching."""
        relationships = set()

        # Clean and normalize text
        text_lower = text.lower()
        sentences = re.split(r'[.!?]', text)

        for sentence in sentences:
            for pattern, rel_type in self.RELATIONSHIP_PATTERNS:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        source, target = match
                        if (source.lower() not in self.STOP_WORDS and
                            target.lower() not in self.STOP_WORDS):
                            rel = Relationship(
                                source=source,
                                target=target,
                                relation_type=rel_type
                            )
                            relationships.add(rel)

        return list(relationships)

    def parse(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        """
        Parse text and extract both entities and relationships.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (entities, relationships)
        """
        entities = self.extract_entities(text)
        relationships = self.extract_relationships(text)
        return entities, relationships


def main():
    """Test the text parser."""
    sample_text = """
    Python is a programming language. Python has many libraries.
    Django is a web framework. Django uses Python.
    Flask is a micro framework. Flask extends Python.
    The User class inherits from BaseModel.
    The database contains tables. Tables have columns.
    """

    parser = TextParser(use_spacy=False)
    entities, relationships = parser.parse(sample_text)

    print("Extracted Entities:")
    for entity in entities:
        print(f"  - {entity.name} ({entity.entity_type})")

    print("\nExtracted Relationships:")
    for rel in relationships:
        print(f"  - {rel.source} --[{rel.relation_type}]--> {rel.target}")


if __name__ == "__main__":
    main()
