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
                # Release Manager
                print("\n" + "="*60)
                print("Release Manager")
                print("="*60)
                
                # Offer to list projects
                list_projects = input("\nDo you want to see a list of available projects? (y/n): ").strip().lower()
                if list_projects == 'y':
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
                
                # Get project key
                project_key = input("\nEnter your Jira project key (e.g., PROJ): ").strip()
                
                if not project_key:
                    print("Error: Project key is required")
                    continue
                
                # Run release manager
                run_release_manager(jira, project_key)
                
            elif choice == '2':
                # Initiative Exporter
                print("\n" + "="*60)
                print("Initiative Exporter")
                print("="*60)
                
                # Offer to list projects
                list_projects = input("\nDo you want to see a list of available projects? (y/n): ").strip().lower()
                if list_projects == 'y':
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
                
                # Get project key
                project_key = input("\nEnter your Jira project key (e.g., PMT): ").strip()
                
                if not project_key:
                    print("Error: Project key is required")
                    continue
                
                # Run initiative exporter
                run_initiative_exporter(jira, project_key)
                
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
