"""
Reference Extraction Utility

Handles the extraction and validation of internal documents and external URLs
from text content. Separated from the main references collector for better
maintainability and testability.
"""

import re
from typing import Dict, List, Set


class ReferenceExtractor:
    """Utility class for extracting and validating references from text."""
    
    def __init__(self):
        self.garbage_patterns = [
            "respuesta final",
            "final response", 
            "answer",
            "response",
            "resultado",
            "output",
            "temp",
            "temporary",
            "test",
            "prueba",
            "ejemplo",
            "example"
        ]
    
    def extract_references(self, text: str) -> Dict[str, List[str]]:
        """
        Extract both internal documents and external URLs from text.
        
        Args:
            text: The text to extract references from
            
        Returns:
            Dict with 'internal' and 'external' lists of references
        """
        if not text:
            return {"internal": [], "external": []}
            
        # Extract internal documents, database sources, and external URLs
        docs = self.extract_documents(text)
        db_sources = self.extract_database_sources(text)
        urls = self.extract_urls(text)
        
        # Combine documents and database sources as internal references
        all_internal = docs + db_sources
        
        return {"internal": all_internal, "external": urls}
    
    def extract_documents(self, text: str) -> List[str]:
        """Extract internal document references (.pptx, .pdf, .docx)."""
        if not text:
            return []
            
        raw_docs = []
        
        # Pattern 1: Quoted filenames "Some Name v2.pptx" (at least 6 chars before extension)
        quoted_docs = re.findall(
            r'"([^"\n]{6,}?\.(?:pptx|pdf|docx))"', text, flags=re.IGNORECASE
        )
        raw_docs.extend(quoted_docs)
        
        # Pattern 2: File paths with manifest/external_data
        file_paths = re.findall(
            r"/[^\n]*(?:manifest|external_data)[^\n]*\.(?:pptx|pdf|docx)",
            text, flags=re.IGNORECASE
        )
        # Extract just the filename from the path
        for path in file_paths:
            filename = path.split("/")[-1]
            if len(filename) > 6:
                raw_docs.append(filename)
        
        # Pattern 3: Documents in REFERENCIAS UTILIZADAS section
        raw_docs.extend(self._extract_from_referencias_section(text))
        
        # Validate, deduplicate, and clean up
        valid_docs = [doc.strip() for doc in raw_docs if self.validate_document(doc.strip())]
        deduplicated_docs = self._deduplicate(valid_docs)
        cleaned_docs = self._remove_suffix_duplicates(deduplicated_docs)
        
        return cleaned_docs
    
    def extract_database_sources(self, text: str) -> List[str]:
        """Extract database source references like 'Databricks Delisoy Sell-In'."""
        if not text:
            return []
            
        db_sources = []
        
        # Look for the specific pattern from the genie wrapper
        pattern = r"\*\*Fuente de datos consultada:\*\*\s*([^\n]+)"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        
        for match in matches:
            source = match.strip()
            if source and len(source) > 3:  # Basic validation
                db_sources.append(source)
        
        return self._deduplicate(db_sources)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract external URL references."""
        if not text:
            return []
            
        urls = re.findall(r"https?://[^\s)\]\"<>]+", text, flags=re.IGNORECASE)
        return self._deduplicate(urls)
    
    def validate_document(self, name: str) -> bool:
        """
        Validate that a document name looks legitimate.
        
        Args:
            name: Document name to validate
            
        Returns:
            True if document name appears valid
        """
        if not name or len(name) < 6:
            return False
            
        # Must have a valid extension
        if not re.search(r"\.(?:pptx|pdf|docx)$", name, re.IGNORECASE):
            return False
            
        base = name.rsplit(".", 1)[0]
        
        # At least 6 characters before extension
        if len(base) < 6:
            return False
            
        # Must include at least one letter
        if not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", base):
            return False
            
        # Filter out garbage patterns
        base_lower = base.lower()
        if any(garbage in base_lower for garbage in self.garbage_patterns):
            return False
            
        # Must look like a real document name (at least 2 meaningful words)
        meaningful_words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,}", base)
        return len(meaningful_words) >= 2
    
    def _extract_from_referencias_section(self, text: str) -> List[str]:
        """Extract documents from REFERENCIAS UTILIZADAS section."""
        referencias_section = re.search(
            r"\*\*REFERENCIAS UTILIZADAS\*\*(.*?)(?=\n\*\*|$)",
            text, re.DOTALL | re.IGNORECASE
        )
        
        if not referencias_section:
            return []
            
        referencias_content = referencias_section.group(1)
        docs = []
        
        for line in referencias_content.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Remove list markers like "1. ", "2. ", "- ", etc.
            clean_line = re.sub(r"^\s*(?:[-\*\d\.]+\s*)", "", line).strip()
            
            # If it's at least 6 chars and looks like a document name
            if len(clean_line) >= 6 and not clean_line.startswith("http"):
                # Add .pptx extension if it doesn't have an extension already
                if not re.search(r"\.(pptx|pdf|docx|ppt)$", clean_line, re.IGNORECASE):
                    clean_line += ".pptx"
                docs.append(clean_line)
        
        return docs
    
    def _deduplicate(self, items: List[str]) -> List[str]:
        """Remove duplicates while preserving order."""
        seen: Set[str] = set()
        result: List[str] = []
        
        for item in items:
            key = item.strip()
            if key and key not in seen:
                seen.add(key)
                result.append(key)
                
        return result
    
    def _remove_suffix_duplicates(self, names: List[str]) -> List[str]:
        """Remove suffix duplicates (e.g., 'II.pptx' if 'Back Data II.pptx' exists)."""
        keep: List[str] = []
        
        for i, name in enumerate(names):
            lower_name = name.lower()
            is_suffix = False
            
            for j, other_name in enumerate(names):
                if i == j:
                    continue
                if other_name.lower().endswith(lower_name) and len(other_name) > len(name) + 2:
                    is_suffix = True
                    break
                    
            if not is_suffix:
                keep.append(name)
                
        return keep
