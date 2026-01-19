from pathlib import Path
import sys
sys.path.insert(0, r'c:\dev\agile_bots\src')

from synchronizers.domain_model import DomainModelOutlineSynchronizer

input_path = Path(r'c:\dev\agile_bots\docs\stories\story-graph.json')
output_path = Path(r'c:\dev\agile_bots\docs\crc\crc-model-outline.md')

synchronizer = DomainModelOutlineSynchronizer()
result = synchronizer.render(input_path, output_path)

print(f'Generated: {result["output_path"]}')
print(f'Domain concepts: {result["summary"]["domain_concepts"]}')
