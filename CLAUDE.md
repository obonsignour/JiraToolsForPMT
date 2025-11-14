# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI tool for managing Jira issues through direct REST API v3 calls. Features include:

1. **Release Manager** - Finds releases containing only Bug issues
2. **Initiative Exporter** - Exports Initiative issues to JSON

## Commands

### Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env
# Then edit .env with your Jira credentials
```

### Running the Tool

```powershell
# Ensure venv is activated first
python sources/jira_tool.py
```

## Architecture

### Core Design Principles

- **No Jira SDK dependencies** - Uses pure REST API v3 calls via `requests` library
- **Lazy initialization** - JiraClient created once when first needed (singleton pattern)
- **Data-driven features** - Menu system uses feature dictionary for extensibility
- **Session-based auth** - Uses `requests.Session` with HTTPBasicAuth for all API calls

### Module Structure

**sources/jira_client.py** - REST API wrapper
- `JiraClient.from_env()` - Creates client from .env variables
- Connection validated on creation by fetching projects
- Methods: `get()`, `post()`, `put()`

**sources/jira_tool.py** - Main entry point
- `get_jira_client()` - Singleton pattern, returns cached client
- `run_feature_workflow()` - Common workflow: header → project list → project key → run feature
- `display_menu()` - Dynamically generates menu from features dict
- Feature configuration in `main()` as dictionary mapping choices to handlers

**sources/release_manager.py** - Release analysis
- Finds "Investment Category" custom field (tries field API, falls back to issue metadata)
- Analyzes releases to find those containing only Bug/Customer bug issues
- JQL: `project = KEY AND fixVersion = "VERSION"`

**sources/initiative_exporter.py** - Initiative export
- Fetches Initiatives using paginated search (nextPageToken)
- JQL: `project = KEY AND issuetype = Initiative AND status NOT IN (DONE, CANCELED)`
- Extracts text from Atlassian Document Format (ADF) for descriptions
- Exports to timestamped JSON: `initiatives_{PROJECT}_{TIMESTAMP}.json`

### Key Implementation Details

**Authentication with Scoped Tokens**
- Uses `session.auth = HTTPBasicAuth(email, api_token)`
- Connection test uses `GET /rest/api/3/project` (works with scoped tokens)
- Cannot use `GET /rest/api/3/myself` - requires different scope

**JQL Search Requirements**
- Must use `POST /rest/api/3/search/jql` (GET is deprecated)
- Always include project restriction in JQL queries
- Pagination via `nextPageToken` for results > 100

**Custom Field Discovery**
- `GET /rest/api/3/field` may not return all custom fields
- Fallback: Fetch issue and use `GET /rest/api/3/issue/{key}/editmeta` to map field IDs to names
- Investment Category field: `customfield_10359` (for PMT project)

**ADF Text Extraction**
- Jira Cloud descriptions use Atlassian Document Format (nested JSON)
- Recursively traverse nodes to extract text content
- `extract_text_from_adf()` handles the conversion

## Adding New Features

To add a new feature to the menu:

1. Create feature module in `sources/` with a `run_feature_name(jira, project_key)` function
2. Import in `jira_tool.py`
3. Add entry to `features` dict in `main()`:
   ```python
   '3': {
       'name': 'Feature Name',
       'description': 'Brief description',
       'runner': run_feature_name,
       'example': 'PROJ'
   }
   ```

The menu system will automatically adapt to the number of features.

## API Endpoints Used

### Common
- `GET /rest/api/3/project` - List projects / connection test

### Release Manager
- `GET /rest/api/3/field` - Get all fields
- `GET /rest/api/3/project/{key}/versions` - Get releases
- `POST /rest/api/3/search/jql` - Search issues with JQL
- `GET /rest/api/3/issue/{key}/editmeta` - Get issue edit metadata

### Initiative Exporter
- `POST /rest/api/3/search/jql` - Search Initiative issues with pagination

## Troubleshooting

**401 Unauthorized**
- Verify API token is valid at https://id.atlassian.com/manage-profile/security/api-tokens
- Check JIRA_EMAIL matches Atlassian account
- Ensure token has issue read/edit scope

**410 Gone on Search**
- Don't use `GET /rest/api/3/search` (deprecated)
- Use `POST /rest/api/3/search/jql` instead

**400 Bad Request - Unbounded JQL**
- Always include `project = KEY` in JQL queries

**Custom Field Not Found**
- Script will fallback to issue metadata extraction
- Field names are case-sensitive
- Some fields only visible in specific projects
