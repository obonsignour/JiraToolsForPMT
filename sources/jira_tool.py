"""
Jira Management Tool - Main Entry Point

This script provides multiple Jira management features:
1. Release Manager - Find releases with only Bug issues
2. Initiative Exporter - Export Initiatives to JSON

Uses Jira Cloud REST API v3 directly.
"""

from typing import List, Dict

from jira_client import JiraClient
from release_manager import run_release_manager
from initiative_exporter import run_initiative_exporter


def get_all_projects(jira: JiraClient) -> List[Dict]:
    """
    Get list of all accessible projects.
    
    Args:
        jira: Authenticated Jira client instance
        
    Returns:
        List of project dictionaries
    """
    try:
        projects = jira.get('rest/api/3/project')
        return projects if isinstance(projects, list) else []
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []


def list_projects_if_requested(jira: JiraClient):
    """
    Optionally list available projects if user requests.
    
    Args:
        jira: Authenticated Jira client instance
    """
    list_choice = input("\nDo you want to see a list of available projects? (y/n): ").strip().lower()
    if list_choice == 'y':
        print("\n📋 Fetching projects...")
        projects = get_all_projects(jira)
        if projects:
            print(f"\nFound {len(projects)} project(s):")
            for proj in projects[:20]:  # Show first 20
                print(f"  • {proj.get('key')}: {proj.get('name')}")
            if len(projects) > 20:
                print(f"  ... and {len(projects) - 20} more projects")
        else:
            print("No projects found or unable to fetch projects.")


def get_project_key_from_user(default_example: str = "PROJ") -> str:
    """
    Prompt user for project key.
    
    Args:
        default_example: Example project key to show in prompt
        
    Returns:
        str: Project key entered by user (stripped), or empty string
    """
    project_key = input(f"\nEnter your Jira project key (e.g., {default_example}): ").strip()
    return project_key


def run_feature_workflow(jira: JiraClient, feature_name: str, feature_runner, default_example: str = "PROJ"):
    """
    Run a feature workflow with common setup (header, project selection).
    
    Args:
        jira: Authenticated Jira client instance
        feature_name: Name of the feature to display
        feature_runner: Function to run the feature (takes jira and project_key)
        default_example: Example project key for the prompt
    """
    display_feature_header(feature_name)
    list_projects_if_requested(jira)
    project_key = get_project_key_from_user(default_example)
    
    if not project_key:
        print("Error: Project key is required")
        return
    
    feature_runner(jira, project_key)


def display_feature_header(title: str):
    """
    Display a feature header.
    
    Args:
        title: Title of the feature
    """
    print("\n" + "="*60)
    print(title)
    print("="*60)


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("Jira Management Tool")
    print("="*60)
    print("\nAvailable Features:")
    print("  1. Release Manager - Find releases with only Bug issues")
    print("  2. Initiative Exporter - Export Initiatives to JSON")
    print("  3. Exit")
    print()


def main():
    """
    Main execution function.
    """
    try:
        # Connect to Jira
        jira = JiraClient.from_env()
        
        while True:
            display_menu()
            choice = input("Select an option (1-3): ").strip()
            
            if choice == '1':
                run_feature_workflow(jira, "Release Manager", run_release_manager, "PROJ")
                
            elif choice == '2':
                run_feature_workflow(jira, "Initiative Exporter", run_initiative_exporter, "PMT")
                
            elif choice == '3':
                print("\nGoodbye!")
                break
            else:
                print("\n⚠️  Invalid option. Please select 1, 2, or 3.")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
