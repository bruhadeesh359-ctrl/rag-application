import re
from typing import List
from abc import ABC, abstractmethod
from app.schemas.domain import DocumentCreate, ChunkCreate, Provenance

class Chunker(ABC):
    @abstractmethod
    def chunk_document(self, document: DocumentCreate) -> List[ChunkCreate]:
        pass

class FixedSizeChunker(Chunker):
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def normalize_text(self, text: str) -> str:
        # Normalize whitespace (replace multiple spaces/newlines with single space)
        # while keeping paragraph boundaries if needed. For now, strict space normalize.
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_document(self, document: DocumentCreate) -> List[ChunkCreate]:
        raw_text = document.raw_content
        if not raw_text or not raw_text.strip():
            # Log this in a real system: "Empty document skipped"
            return []

        normalized_text = self.normalize_text(raw_text)
        if not normalized_text:
            return []

        words = normalized_text.split()
        chunks = []
        current_chunk_words = []
        current_length = 0
        chunk_index = 0
        
        word_idx = 0
        while word_idx < len(words):
            word = words[word_idx]
            current_chunk_words.append(word)
            current_length += len(word) + 1 # +1 for space
            
            if current_length >= self.chunk_size or word_idx == len(words) - 1:
                chunk_text = " ".join(current_chunk_words)
                
                provenance = Provenance(
                    document_id=document.document_id,
                    filename=document.metadata.filename,
                    chunk_index=chunk_index,
                    page=document.metadata.additional_info.get("page", None),
                    section=document.metadata.additional_info.get("section", None),
                    source_location=f"chunk_{chunk_index}"
                )
                
                chunks.append(ChunkCreate(
                    chunk_id=f"{document.document_id}_chunk_{chunk_index:03d}",
                    document_id=document.document_id,
                    text=chunk_text,
                    provenance=provenance
                ))
                
                chunk_index += 1
                
                # Handle Overlap deterministically
                if word_idx < len(words) - 1 and self.overlap > 0:
                    overlap_chars = 0
                    overlap_words = []
                    # Backtrack safely
                    for w in reversed(current_chunk_words):
                        # Calculate length if we add this word
                        if overlap_chars + len(w) + 1 > self.overlap:
                            # At least one word for overlap if possible, but respect limit strictly
                            if not overlap_words:
                                overlap_words.insert(0, w)
                                overlap_chars += len(w) + 1
                            break
                        overlap_words.insert(0, w)
                        overlap_chars += len(w) + 1
                        
                    current_chunk_words = overlap_words
                    current_length = sum(len(w) + 1 for w in current_chunk_words)
                else:
                    current_chunk_words = []
                    current_length = 0
            
            word_idx += 1
            
        return chunks
