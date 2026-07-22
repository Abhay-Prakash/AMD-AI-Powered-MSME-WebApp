import re


class DocumentCleaner:
    def clean(self, text: str) -> str:
        """Cleans extracted text by normalizing whitespace, merging wrapped lines, and removing typical junk."""
        if not text:
            return ""

        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip page numbers (e.g., "Page 1 of 10", "- 1 -", "1")
            if re.match(r'^page\s+\d+(\s+of\s+\d+)?$', line, re.IGNORECASE):
                continue
            if re.match(r'^-\s*\d+\s*-$', line):
                continue
            if re.match(r'^\d+$', line):
                continue
                
            # If the line is empty, just keep it to preserve paragraphs
            if not line:
                cleaned_lines.append("")
                continue
                
            cleaned_lines.append(line)
            
        # Reconstruct text
        text = "\n".join(cleaned_lines)
        
        # Merge wrapped lines (lines that don't end with punctuation)
        # This is tricky because it might merge table contents. We'll do a conservative merge.
        # If a line doesn't end with a period, colon, or semicolon, and the next line isn't empty, merge them.
        merged_text = re.sub(r'([^\.\:;\n])\n([^\n])', r'\1 \2', text)
        
        # Remove duplicate blank lines (more than 2 consecutive newlines)
        merged_text = re.sub(r'\n{3,}', '\n\n', merged_text)
        
        return merged_text.strip()
