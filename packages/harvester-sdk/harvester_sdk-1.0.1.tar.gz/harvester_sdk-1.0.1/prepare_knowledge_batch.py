#!/usr/bin/env python3
"""
Prepare knowledge extraction batch CSV from markdown files
"""

import csv
import json
from pathlib import Path
from jinja2 import Template

# Knowledge extraction template
KNOWLEDGE_TEMPLATE = """You are analyzing technical documentation about {{ filename }}.

Content:
\"\"\"
{{ content }}
\"\"\"

Based on this content, please:

1. Generate 3 insightful technical questions that test deep understanding of the concepts presented. Questions should be specific and answerable from the content.

2. Provide a comprehensive technical summary (one detailed paragraph) including:
   - Key concepts and definitions
   - Important technical details  
   - Practical applications or use cases
   - Relevant considerations or best practices

3. Extract the most important technical insights or takeaways.

Format your response as JSON with the following structure:
{
  "topic": "{{ filename }}",
  "questions": [
    "Question 1 here",
    "Question 2 here", 
    "Question 3 here"
  ],
  "summary": "Comprehensive paragraph summary here",
  "key_insights": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ]
}"""

def prepare_knowledge_batch(input_dir: Path, output_csv: Path):
    """
    Prepare CSV for batch processing of knowledge files
    """
    # Get all markdown files
    md_files = sorted(input_dir.glob("*.md"))
    
    print(f"Found {len(md_files)} markdown files")
    
    # Prepare template
    template = Template(KNOWLEDGE_TEMPLATE)
    
    # Create CSV rows
    rows = []
    for i, md_file in enumerate(md_files):
        # Read file content
        content = md_file.read_text(encoding='utf-8')
        
        # Create prompt from template
        prompt = template.render(
            filename=md_file.name,
            content=content
        )
        
        # Add row
        rows.append({
            'custom_id': f'knowledge-{i+1:03d}',
            'prompt': prompt,
            'model': 'gpt-5-nano',  # Can be overridden
            'reasoning_effort': 'medium',
            'verbosity': 'medium',
            'max_tokens': 1000,
            'source_file': md_file.name
        })
        
        print(f"  - Processed: {md_file.name}")
    
    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['custom_id', 'prompt', 'model', 'reasoning_effort', 'verbosity', 'max_tokens', 'source_file']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✅ Created batch CSV: {output_csv}")
    print(f"📊 Total prompts: {len(rows)}")
    print(f"💡 Each prompt will generate 3 questions + 1 summary paragraph")
    print(f"\nTo submit for batch processing:")
    print(f"  ./venv/bin/python batch_submit.py {output_csv} --provider openai --wait")
    
    return len(rows)

if __name__ == "__main__":
    # Process the 5G edge computing files
    input_dir = Path("/home/rich/productions/knowledge-query-system/knowledge-queries-extracted/5g_edge_computing")
    output_csv = Path("5g_knowledge_batch.csv")
    
    prepare_knowledge_batch(input_dir, output_csv)