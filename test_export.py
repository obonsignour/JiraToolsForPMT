"""Quick test script for Initiative exporter"""
import sys
sys.path.insert(0, 'sources')

from jira_client import JiraClient
from initiative_exporter import export_initiatives_to_json

# Connect to Jira
jira = JiraClient.from_env()
print(f"✓ Connected to Jira")

# Export initiatives
output_file = export_initiatives_to_json(jira, 'PMT')
print(f"\n✓ Export complete: {output_file}")

# Show a sample record
if output_file:
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Find an initiative with linked issues
        for item in data:
            if item.get('linkedIssuesCount', 0) > 0:
                print(f"\nSample Initiative with linked issues:")
                print(json.dumps(item, indent=2))
                break
