import sys
import re

file_path = r'C:\Users\bruha\.gemini\antigravity\scratch\rag-observability-lab\backend\app\services\rag_service.py'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

pattern = r'# BYPASS LLM OUTAGE.*?return \{.*?\n            \}'
replacement = '''# BYPASS LLM OUTAGE
            fallback_answer = \"Google API Outage (503). Retrieved evidence:\\n\\n\"
            
            frontend_citations = []
            for i, chunk in enumerate(retrieved_chunks):
                token = f\"S{i+1}\"
                fallback_answer += f\"- '{chunk.text.strip()[:200]}...' [{token}]\\n\\n\"
                
                frontend_citations.append({
                    'token': token,
                    'document_id': chunk.document_id,
                    'filename': chunk.provenance.filename if chunk.provenance else chunk.document_id,
                    'page': chunk.provenance.page if chunk.provenance else None,
                    'text': chunk.text
                })
            
            return {
                \"query\": question,
                \"answer\": fallback_answer.strip(),
                \"status\": \"partial\",
                \"citations\": frontend_citations,
                \"retrieval\": {
                    \"chunks\": len(retrieved_chunks),
                    \"time_ms\": timings.get(\"retrieval_ms\", 0)
                },
                \"generation\": {
                    \"time_ms\": 0,
                    \"model\": \"fallback\"
                }
            }'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
