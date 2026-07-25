import re

with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

words = re.findall(r'\b\w+\b', text.lower())
total_words = len(words)

keywords = [
    'flowchart ai generator',
    'flowchart ai',
    'draw.io mcp',
    'drawio mcp',
    'google antigravity mcp',
    'google antigravity',
    'architecture diagram ai',
    'antigravity-drawio-mcp',
    'mermaid to drawio',
    'mcp'
]

print(f"Total Word Count: {total_words}")
for kw in keywords:
    count = len(re.findall(re.escape(kw), text, re.IGNORECASE))
    kw_words = len(re.findall(r'\b\w+\b', kw))
    density = (count * kw_words / total_words) * 100
    print(f"Keyword: '{kw}' | Occurrences: {count} | Density: {density:.2f}%")
