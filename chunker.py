import re
import tiktoken


class DocumentChunker:
    def __init__(self, max_tokens: int = 500, overlap_tokens: int = 50, model_name: str = "cl100k_base"):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding = tiktoken.get_encoding(model_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk(self, text: str, base_metadata: dict) -> list[dict]:
        """
        Structure-aware chunker with token-aware fallback.
        Attempts to split by paragraphs/sections first.
        """
        chunks = []
        
        # Split by paragraphs (double newlines)
        paragraphs = re.split(r'\n\n+', text)
        
        current_chunk_text = ""
        current_tokens = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            para_tokens = self.count_tokens(para)
            
            # If a single paragraph is too large, we must fall back to token-level splitting
            if para_tokens > self.max_tokens:
                # Flush the current chunk if it exists
                if current_chunk_text:
                    chunks.append({
                        "chunk_index": chunk_index,
                        "content": current_chunk_text.strip(),
                        "metadata": base_metadata.copy()
                    })
                    chunk_index += 1
                    current_chunk_text = ""
                    current_tokens = 0
                
                # Split the massive paragraph by tokens
                para_token_ids = self.encoding.encode(para)
                for i in range(0, len(para_token_ids), self.max_tokens - self.overlap_tokens):
                    slice_ids = para_token_ids[i:i + self.max_tokens]
                    slice_text = self.encoding.decode(slice_ids)
                    chunks.append({
                        "chunk_index": chunk_index,
                        "content": slice_text.strip(),
                        "metadata": base_metadata.copy()
                    })
                    chunk_index += 1
                continue
            
            # If adding this paragraph exceeds the limit, flush the current chunk
            if current_tokens + para_tokens > self.max_tokens and current_chunk_text:
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": current_chunk_text.strip(),
                    "metadata": base_metadata.copy()
                })
                chunk_index += 1
                current_chunk_text = ""
                current_tokens = 0
                
            # Add paragraph to current chunk
            current_chunk_text += ("\n\n" + para if current_chunk_text else para)
            current_tokens = self.count_tokens(current_chunk_text)
            
        # Flush the last chunk
        if current_chunk_text:
            chunks.append({
                "chunk_index": chunk_index,
                "content": current_chunk_text.strip(),
                "metadata": base_metadata.copy()
            })
            
        return chunks
