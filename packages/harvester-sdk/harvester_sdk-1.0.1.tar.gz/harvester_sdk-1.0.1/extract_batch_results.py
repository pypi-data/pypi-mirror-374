#!/usr/bin/env python3
"""
Extract and display batch processing results
"""

import json
import re

# Load the JSON results
with open('/home/rich/harvester-sdk/batch_submit/5g_knowledge_batch_20250906_100109/batch_batch_68bbea472b508190afd203d0cccab0e4_results.json', 'r') as f:
    results = json.load(f)

print(f'✅ Successfully processed {len(results)} files\n')
print('='*80)

for i, result in enumerate(results, 1):
    custom_id = result.get('custom_id', 'Unknown')
    content = result.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
    
    # Remove markdown code blocks if present
    content = re.sub(r'^```json\n', '', content)
    content = re.sub(r'\n```$', '', content)
    content = content.strip()
    
    try:
        # Parse the JSON response
        parsed = json.loads(content)
        topic = parsed.get('topic', 'Unknown')
        questions = parsed.get('questions', [])
        summary = parsed.get('summary', '')
        insights = parsed.get('key_insights', [])
        
        print(f'\n📄 File {i}: {topic}')
        print('-'*60)
        
        print('\n🤔 Generated Questions:')
        for j, q in enumerate(questions, 1):
            print(f'\n  Question {j}:')
            print(f'  {q}')
        
        print(f'\n📝 Summary:')
        # Print full summary with word wrap
        words = summary.split()
        line = '  '
        for word in words:
            if len(line) + len(word) > 78:
                print(line)
                line = '  ' + word
            else:
                line += ' ' + word if line != '  ' else word
        if line.strip():
            print(line)
        
        if insights:
            print(f'\n💡 Key Insights:')
            for insight in insights:
                print(f'  • {insight}')
        
        print('\n' + '='*80)
        
    except json.JSONDecodeError as e:
        print(f'\n❌ Error parsing response for {custom_id}: {e}')
        print(f'Content preview: {content[:200]}...')
        continue

print('\n✨ All results extracted successfully!')
print(f'📁 Results saved in: /home/rich/harvester-sdk/batch_submit/5g_knowledge_batch_20250906_100109/')