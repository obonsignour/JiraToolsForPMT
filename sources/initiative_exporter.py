"""
Initiative Exporter - Export Initiatives to JSON

This module exports Initiative issues from a Jira project to a JSON file.
Includes issue key, description, requester, and linked issue count.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime

from jira_client import JiraClient


def get_initiatives(jira: JiraClient, project_key: str) -> List[Dict]:
    """
    Get all Initiative issues from a project that are not DONE or CANCELED.
    Handles pagination using nextPageToken (max 100 results per page).
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to search
        
    Returns:
        List[Dict]: List of Initiative issues with required fields
    """
    print(f"\n🔍 Fetching Initiatives from project {project_key}...")
    
    try:
        # JQL to find Initiatives that are not DONE or CANCELED
        jql = f'project = {project_key} AND issuetype = Initiative AND status NOT IN (DONE, CANCELED)'
        
        all_issues = []
        next_page_token = None
        page_num = 1
        
        # Fetch all pages using token-based pagination
        while True:
            print(f"  Fetching page {page_num}...", end='')
            
            # Build request data
            request_data = {
                'jql': jql,
                'maxResults': 100,  # API limit per page
                'fields': ['summary', 'description', 'reporter', 'issuelinks', 'fixVersions', 'versions'],
                'expand': 'issuelinks'  # Expand to get linked issue details
            }
            
            # Add nextPageToken if this is not the first page
            if next_page_token:
                request_data['nextPageToken'] = next_page_token
            
            # Fetch page
            result = jira.post('rest/api/3/search/jql', data=request_data)
            
            # Collect issues from this page
            page_issues = result.get('issues', [])
            all_issues.extend(page_issues)
            print(f" {len(page_issues)} issues")
            
            # Check if this is the last page
            is_last = result.get('isLast', True)
            if is_last:
                break
            
            # Get token for next page
            next_page_token = result.get('nextPageToken')
            if not next_page_token:
                # No token but not last page - shouldn't happen, but break to be safe
                print("  ⚠️  Warning: No nextPageToken but isLast is False")
                break
            
            page_num += 1
        
        print(f"✓ Found {len(all_issues)} Initiative(s) across {page_num} page(s)")
        
        return all_issues
    except Exception as e:
        print(f"❌ Error fetching Initiatives: {e}")
        return []


def format_initiative_data(issue: Dict) -> Dict:
    """
    Format Initiative issue data for export.
    
    Args:
        issue: Raw Jira issue dictionary
        
    Returns:
        Dict: Formatted issue data with required fields
    """
    fields = issue.get('fields', {})
    
    # Get issue key
    issue_key = issue.get('key', '')
    
    # Get description (can be in various formats)
    description_obj = fields.get('description')
    if description_obj:
        # Jira Cloud uses Atlassian Document Format (ADF)
        if isinstance(description_obj, dict):
            # Try to extract text from ADF
            description = extract_text_from_adf(description_obj)
        else:
            description = str(description_obj)
    else:
        description = ""
    
    # Get requester (reporter)
    reporter = fields.get('reporter', {})
    if reporter:
        requester = reporter.get('displayName', reporter.get('emailAddress', 'Unknown'))
    else:
        requester = "Unknown"
    
    # Process linked issues
    issue_links = fields.get('issuelinks', [])
    linked_issues_count = len(issue_links)
    
    # Extract linked issue details
    linked_issues_details = []
    for link in issue_links:
        # Linked issue can be inward or outward
        linked_issue = link.get('inwardIssue') or link.get('outwardIssue')
        if linked_issue:
            linked_fields = linked_issue.get('fields', {})
            issue_type = linked_fields.get('issuetype', {})
            
            linked_issues_details.append({
                'key': linked_issue.get('key', ''),
                'summary': linked_fields.get('summary', ''),
                'issueType': issue_type.get('name', '')
            })
    
    # Get fix versions
    fix_versions = fields.get('fixVersions', [])
    fix_version_names = [v.get('name', '') for v in fix_versions] if fix_versions else []
    
    # Get affected versions (versions field)
    affected_versions = fields.get('versions', [])
    affected_version_names = [v.get('name', '') for v in affected_versions] if affected_versions else []
    
    return {
        'issueKey': issue_key,
        'description': description,
        'requester': requester,
        'linkedIssuesCount': linked_issues_count,
        'linkedIssues': linked_issues_details,
        'fixVersions': fix_version_names,
        'affectedVersions': affected_version_names
    }


def extract_text_from_adf(adf: Dict) -> str:
    """
    Extract plain text from Atlassian Document Format (ADF).
    
    Args:
        adf: ADF document structure
        
    Returns:
        str: Extracted plain text
    """
    def extract_from_node(node):
        if not isinstance(node, dict):
            return ""
        
        # If node has text, return it
        if 'text' in node:
            return node['text']
        
        # If node has content, recursively extract from children
        content = node.get('content', [])
        texts = []
        for child in content:
            text = extract_from_node(child)
            if text:
                texts.append(text)
        
        return ' '.join(texts)
    
    return extract_from_node(adf).strip()


def export_initiatives_to_json(jira: JiraClient, project_key: str, output_file: Optional[str] = None) -> str:
    """
    Export Initiatives to a JSON file.
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to export from
        output_file: Optional output filename (defaults to initiatives_{project_key}_{timestamp}.json)
        
    Returns:
        str: Path to the created JSON file
    """
    # Get initiatives
    issues = get_initiatives(jira, project_key)
    
    if not issues:
        print("⚠️  No Initiatives found to export.")
        return ""
    
    # Format data
    print(f"\n📝 Formatting Initiative data...")
    formatted_data = []
    for issue in issues:
        formatted_data.append(format_initiative_data(issue))
    
    # Generate filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'initiatives_{project_key}_{timestamp}.json'
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully exported {len(formatted_data)} Initiative(s) to: {output_file}")
        return output_file
    except Exception as e:
        print(f"\n❌ Error writing JSON file: {e}")
        return ""


def run_initiative_exporter(jira: JiraClient, project_key: str):
    """
    Run the initiative exporter workflow.
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to export from
    """
    print(f"\n{'='*60}")
    print(f"Initiative Exporter - Project: {project_key}")
    print(f"{'='*60}")
    
    output_file = export_initiatives_to_json(jira, project_key)
    
    if output_file:
        print(f"\n{'='*60}")
        print(f"Export Complete!")
        print(f"{'='*60}")
        print(f"\nFile: {output_file}")
        print(f"\nThe JSON file contains:")
        print(f"  - issueKey: The Jira issue key")
        print(f"  - description: The issue description")
        print(f"  - requester: The issue reporter/requester")
        print(f"  - linkedIssuesCount: Number of linked issues")
        print(f"  - linkedIssues: Array of linked issues with key, summary, and issueType")
        print(f"  - fixVersions: List of fix version names")
        print(f"  - affectedVersions: List of affected version names")
