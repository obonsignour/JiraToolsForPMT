# Python Jira Management Tool Project

## Project Overview

Python tool for managing Jira issues with multiple features:

1. **Release Manager** - Find releases containing only Bug issues and update Investment Category field
2. **Initiative Exporter** - Export Initiative issues to JSON file

Uses **Jira Cloud REST API v3 directly** without any external Jira library dependencies.

## Technology Stack

- Python 3.x
- **Pure REST API**: Direct HTTP calls to Jira Cloud API v3
- `requests` library for HTTP communication
- `python-dotenv` for environment variable management
- Virtual environment for dependency management

## Project Structure

- `sources/` - Python source files folder
  - `jira_tool.py` - Main entry point with menu system
  - `jira_client.py` - Jira REST API v3 client with connection management
  - `release_manager.py` - Release management features
  - `initiative_exporter.py` - Initiative export to JSON functionality
- `requirements.txt` - Python dependencies (requests, python-dotenv)
- `.env` - Environment variables for Jira credentials (not committed)
- `.env.example` - Template for environment variables
- `.gitignore` - Git ignore patterns
- `README.md` - Project documentation

## Development Guidelines

- Use Python virtual environment for all development
- Store Jira credentials in environment variables
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- **Use only direct REST API calls** - no Jira SDK/library dependencies
- All API calls go through the JiraClient wrapper class

## Architecture

### Modules

#### jira_client.py

Simple REST API wrapper with methods:

- `__init__(url, email, api_token)` - Direct instantiation
- `from_env()` - Class method to create from environment variables
- `get(endpoint, params)` - GET requests
- `post(endpoint, data)` - POST requests
- `put(endpoint, data)` - PUT requests

#### release_manager.py

Release management functionality:

- `get_investment_category_field_id()` - Find custom field ID
- `get_all_releases()` - Get project releases
- `check_release_has_only_bugs()` - Validate release content
- `find_qualifying_releases()` - Find releases with only bugs
- `run_release_manager()` - Execute release manager workflow

#### initiative_exporter.py

Initiative export functionality:

- `get_initiatives()` - Fetch Initiative issues (not DONE/CANCELED)
- `format_initiative_data()` - Format issue data for export
- `extract_text_from_adf()` - Extract text from Atlassian Document Format
- `export_initiatives_to_json()` - Export to JSON file
- `run_initiative_exporter()` - Execute exporter workflow

#### jira_tool.py

Main entry point:

- `get_all_projects()` - List accessible projects
- `display_menu()` - Show feature menu
- `main()` - Main execution loop

### API Endpoints Used

#### Common

- `GET /rest/api/3/project` - List projects / connection test

#### Release Manager

- `GET /rest/api/3/field` - Get all fields
- `GET /rest/api/3/project/{key}/versions` - Get releases
- `POST /rest/api/3/search/jql` - Search issues with JQL
- `GET /rest/api/3/issue/{key}/editmeta` - Get issue metadata

#### Initiative Exporter

- `POST /rest/api/3/search/jql` - Search Initiative issues

## Completed Steps

### Core Infrastructure

- [x] Created project structure and copilot-instructions.md
- [x] Set up Python virtual environment
- [x] Installed dependencies (requests, python-dotenv)
- [x] Created JiraClient class for REST API access
- [x] Implemented connection and authentication with scoped tokens
- [x] Refactored JiraClient to separate file with from_env() class method

### Release Manager (Phase 1)

- [x] Added project listing functionality
- [x] Added custom field discovery (with fallback to issue metadata)
- [x] Added release analysis logic
- [x] Added issue type filtering (Bug/Customer bug only)
- [x] Moved to dedicated release_manager.py module
- [x] Integrated into menu system

### Initiative Exporter (Phase 1)

- [x] Created initiative_exporter.py module
- [x] Implemented Initiative fetching with status filter
- [x] Added ADF (Atlassian Document Format) text extraction
- [x] Implemented JSON export with timestamps
- [x] Integrated into menu system

### Documentation

- [x] Created comprehensive README documentation
- [x] Updated copilot-instructions.md with new structure

## Important Implementation Details

### Authentication & Scoped Tokens

- **Jira Instance**: https://cast-products.atlassian.net
- **User**: o.bonsignour@castsoftware.com
- **Token Scope**: Issue read/edit only (scoped token)
- **Connection Test**: Uses `GET /rest/api/3/project` (works with scoped tokens)
- **Note**: Cannot use `GET /rest/api/3/myself` - requires different scope

### JQL Search Requirements

- Must use `POST /rest/api/3/search/jql` (not GET)
- `GET /rest/api/3/search` is deprecated (returns 410 Gone)
- JQL queries must have project restrictions (unbounded queries not allowed)
- Example: `project = PMT AND issuetype = Initiative`

### Custom Field Discovery

- `GET /rest/api/3/field` may not return all custom fields
- Fallback: Extract from issue metadata using `GET /rest/api/3/issue/{key}/editmeta`
- Investment Category field ID: `customfield_10359` (for PMT project)

### Session-Based Authentication

- Uses `requests.Session` with `session.auth = HTTPBasicAuth(email, token)`
- Auth credentials automatically included in all session requests
- No need to pass auth parameter to each request

## Current State (2025-11-12)

### Working Features

1. **JiraClient** - Fully functional with:

   - `from_env()` class method for easy instantiation
   - Proper error handling and debugging
   - Scoped token support

2. **Release Manager** - Operational:

   - Lists all releases in project
   - Filters by issue type (Bug/Customer bug only)
   - Finds Investment Category custom field
   - Shows qualifying releases
   - Ready for Phase 2 (update functionality)

3. **Initiative Exporter** - Operational:

   - Fetches Initiatives (excludes DONE/CANCELED)
   - Extracts text from Atlassian Document Format (ADF)
   - Exports to JSON with: issueKey, description, requester, linkedIssuesCount
   - Generates timestamped files: `initiatives_{PROJECT}_{TIMESTAMP}.json`

4. **Menu System** - Working:
   - Interactive menu with 3 options
   - Loops until user exits
   - Both features accessible independently

### Known Issues & Limitations

- No known issues at this time
- Both features tested and working
- Project PMT confirmed accessible with 30 releases

### Test Projects

- **PMT** - Primary test project (has 30 releases, 260 projects accessible)
- **MCP** - Secondary test project (0 Initiatives found)

## Next Phase (Phase 2)

### Release Manager Updates

- [ ] Add functionality to update "Investment Category" field
- [ ] Find Release issues by version number (issuetype='Release')
- [ ] Update field to "Product Growth (Offense)"
- [ ] Add dry-run mode (show changes without applying)
- [ ] Add confirmation prompt before updates
- [ ] Add logging and reporting of changes made

## Troubleshooting Guide

### Common Issues

1. **401 Unauthorized**

   - Check API token is valid and not expired
   - Verify JIRA_EMAIL matches Atlassian account
   - Ensure token has issue read/edit scope

2. **404 Not Found on Project**

   - Project key may not exist
   - Token may not have access to that project
   - Try listing projects first to see accessible projects

3. **410 Gone on Search**

   - Don't use GET /rest/api/3/search (deprecated)
   - Use POST /rest/api/3/search/jql instead

4. **400 Bad Request - Unbounded JQL**

   - Always include project restriction in JQL
   - Example: `project = KEY AND ...`

5. **Custom Field Not Found**
   - Use fallback to issue metadata
   - Check field name spelling (case-sensitive)
   - Field may only be visible in specific projects

## Usage Examples

### Run the Tool

```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Run main script
python sources/jira_tool.py
```

### Menu Options

1. **Release Manager** - Analyze releases for Bug-only content
2. **Initiative Exporter** - Export Initiatives to JSON
3. **Exit** - Quit application

### Output Files

- Initiative exports: `initiatives_{PROJECT}_{TIMESTAMP}.json`
- Located in project root directory
