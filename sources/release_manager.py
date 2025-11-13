"""
Release Manager - Find and update releases with only Bug issues

This module provides functionality to identify releases that contain only
"Bug" or "Customer bug" issue types and update their Investment Category field.
"""

from typing import List, Dict, Set, Optional

from jira_client import JiraClient


def get_investment_category_field_id(jira: JiraClient, project_key: str) -> str:
    """
    Find the custom field ID for "Investment Category".
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to help search
        
    Returns:
        str: The custom field ID (e.g., 'customfield_10001')
    """
    # Get all fields using REST API v3
    all_fields = jira.get('rest/api/3/field')
    
    if not all_fields or not isinstance(all_fields, list):
        print(f"⚠️ Failed to retrieve fields from Jira API")
        all_fields = []
    
    print(f"📋 Searching through {len(all_fields)} fields...")
    
    # Debug: print field types
    if all_fields:
        custom_count = sum(1 for f in all_fields if isinstance(f, dict) and f.get('id', '').startswith('customfield_'))
        system_count = len(all_fields) - custom_count
        print(f"   ({system_count} system fields, {custom_count} custom fields)")
    
    # First, try exact match
    for field in all_fields:
        if field.get('name') == 'Investment Category':
            print(f"✓ Found 'Investment Category' field: {field['id']}")
            return field['id']
    
    # If not found, try case-insensitive search
    for field in all_fields:
        if field.get('name', '').lower() == 'investment category':
            print(f"✓ Found 'Investment Category' field (case mismatch): {field['id']}")
            return field['id']
    
    # If still not found, try partial match and show custom fields
    print("\n⚠️  Could not find 'Investment Category' field.")
    print("📋 Available custom fields:")
    custom_fields = [f for f in all_fields if f.get('id', '').startswith('customfield_')]
    
    if custom_fields:
        print(f"  Found {len(custom_fields)} custom fields. Showing all that contain 'invest' or 'category':")
        matching = [f for f in custom_fields if 'invest' in f.get('name', '').lower() or 'category' in f.get('name', '').lower()]
        if matching:
            for field in matching:
                print(f"  ✓ {field.get('name')}: {field.get('id')}")
        
        print(f"\n  All custom fields (first 30):")
        for field in custom_fields[:30]:
            print(f"  - {field.get('name')}: {field.get('id')}")
        if len(custom_fields) > 30:
            print(f"  ... and {len(custom_fields) - 30} more custom fields")
    else:
        print("  No custom fields found in field list!")
    
    # Try to get field from an actual issue
    print(f"\n🔍 Attempting to find field from a sample issue in {project_key}...")
    try:
        # Search for issues using JQL (POST required for /search/jql)
        response = jira.post('rest/api/3/search/jql', data={
            'jql': f'project = {project_key}',
            'maxResults': 1,
            'fields': ['*all']
        })
        
        issues = response.get('issues', [])
        if issues:
            issue = issues[0]
            issue_key = issue.get('key')
            print(f"  Examining issue: {issue_key}")
            
            # Get raw fields
            raw_fields = issue.get('fields', {})
            print(f"  Found {len(raw_fields)} fields in issue")
            
            # Get issue metadata to map field IDs to names
            print(f"  Fetching edit metadata for field names...")
            meta_response = jira.get(f'rest/api/3/issue/{issue_key}/editmeta')
            
            field_names_map = {}
            fields_meta = meta_response.get('fields', {})
            for field_id, field_info in fields_meta.items():
                field_names_map[field_id] = field_info.get('name', '')
            
            print(f"  Retrieved {len(field_names_map)} editable field names")
            
            # Look for investment category
            custom_fields_found = []
            for field_id in raw_fields.keys():
                if field_id.startswith('customfield_'):
                    field_name = field_names_map.get(field_id, '')
                    if field_name:
                        custom_fields_found.append((field_id, field_name))
                        if 'investment' in field_name.lower() and 'category' in field_name.lower():
                            print(f"✓ Found via issue: '{field_name}' = {field_id}")
                            return field_id
            
            # Show custom fields found
            if custom_fields_found:
                print(f"\n  📋 Found {len(custom_fields_found)} editable custom fields in issue:")
                for fid, fname in custom_fields_found[:20]:
                    print(f"    - {fname}: {fid}")
                if len(custom_fields_found) > 20:
                    print(f"    ... and {len(custom_fields_found) - 20} more")
            else:
                print(f"  ⚠️ No custom fields found in issue metadata")
        else:
            print(f"  No issues found in project {project_key}")
    except Exception as e:
        print(f"  Error searching issues: {type(e).__name__}: {str(e)}")
    
    print("\n❌ Could not find 'Investment Category' custom field.")
    print("Please check the exact field name in Jira and update the script.")
    raise ValueError("Could not find 'Investment Category' custom field")


def get_all_releases(jira: JiraClient, project_key: str) -> List[Dict]:
    """
    Retrieve all releases (fixVersions) from Jira using REST API.
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to get releases for
        
    Returns:
        List[Dict]: List of release information dictionaries
    """
    try:
        # Get releases for a specific project using REST API v3
        releases = jira.get(f'rest/api/3/project/{project_key}/versions')
        if releases and isinstance(releases, list):
            print(f"✓ Found {len(releases)} releases in project {project_key}")
            return releases
        else:
            print(f"⚠️ No releases found for project {project_key}")
            return []
    except Exception as e:
        print(f"❌ Error fetching releases: {e}")
        return []


def get_issues_in_release(jira: JiraClient, release_name: str, project_key: str) -> List[Dict]:
    """
    Get all issues associated with a specific release using REST API.
    
    Args:
        jira: Authenticated Jira client instance
        release_name: Name of the release version
        project_key: Project key
        
    Returns:
        List[Dict]: List of Jira issues in the release
    """
    try:
        jql = f'project = {project_key} AND fixVersion = "{release_name}"'
        result = jira.post('rest/api/3/search/jql', data={
            'jql': jql,
            'maxResults': 1000,
            'fields': ['issuetype']
        })
        return result.get('issues', [])
    except Exception as e:
        print(f"Error fetching issues for release {release_name}: {e}")
        return []


def check_release_has_only_bugs(jira: JiraClient, release_name: str, project_key: str) -> Dict:
    """
    Check if a release contains only "Bug" or "Customer bug" issue types.
    
    Args:
        jira: Authenticated Jira client instance
        release_name: Name of the release version
        project_key: Project key
        
    Returns:
        Dict: Dictionary with release info and whether it qualifies
    """
    issues = get_issues_in_release(jira, release_name, project_key)
    
    if not issues:
        return {
            'release': release_name,
            'qualifies': False,
            'reason': 'No issues found',
            'issue_types': set(),
            'issue_count': 0
        }
    
    issue_types = set()
    allowed_types = {'Bug', 'Customer bug'}
    
    for issue in issues:
        issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', '')
        if issue_type:
            issue_types.add(issue_type)
    
    qualifies = issue_types.issubset(allowed_types) and len(issue_types) > 0
    
    return {
        'release': release_name,
        'qualifies': qualifies,
        'reason': 'Only bugs' if qualifies else f'Contains other issue types: {issue_types - allowed_types}',
        'issue_types': issue_types,
        'issue_count': len(issues)
    }


def find_qualifying_releases(jira: JiraClient, project_key: str) -> List[Dict]:
    """
    Find all releases that contain only Bug or Customer bug issues.
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to search
        
    Returns:
        List[Dict]: List of qualifying releases with details
    """
    print(f"\n🔍 Analyzing releases in project {project_key}...")
    
    versions = get_all_releases(jira, project_key)
    qualifying_releases = []
    
    for version in versions:
        version_name = version.get('name', '')
        if not version_name:
            continue
            
        result = check_release_has_only_bugs(jira, version_name, project_key)
        
        if result['qualifies']:
            qualifying_releases.append(result)
            print(f"  ✓ {result['release']}: {result['issue_count']} issues - {result['issue_types']}")
        else:
            print(f"  ✗ {result['release']}: {result['reason']}")
    
    return qualifying_releases


def run_release_manager(jira: JiraClient, project_key: str):
    """
    Run the release manager workflow.
    
    Args:
        jira: Authenticated Jira client instance
        project_key: Project key to analyze
    """
    # Get the Investment Category field ID
    try:
        investment_category_field = get_investment_category_field_id(jira, project_key)
    except ValueError as e:
        print(f"\n⚠️  {str(e)}")
        manual_field = input("\nDo you know the custom field ID? Enter it (e.g., customfield_10001) or press Enter to skip: ").strip()
        if manual_field:
            investment_category_field = manual_field
            print(f"✓ Using custom field: {investment_category_field}")
        else:
            print("⚠️  Continuing without custom field ID (will find releases only)")
            investment_category_field = None
    
    # Find qualifying releases
    qualifying_releases = find_qualifying_releases(jira, project_key)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary: Found {len(qualifying_releases)} qualifying release(s)")
    print(f"{'='*60}")
    
    if qualifying_releases:
        print("\nQualifying releases (contain only Bug/Customer bug issues):")
        for release in qualifying_releases:
            print(f"  • {release['release']} ({release['issue_count']} issues)")
    else:
        print("\nNo qualifying releases found.")
    
    if investment_category_field:
        print(f"\nNext step: These releases can be updated with Investment Category = 'Product Growth (Offense)'")
        print(f"Investment Category field ID: {investment_category_field}")
