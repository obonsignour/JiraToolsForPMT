# Jira Management Tool

Python tool for managing Jira issues with multiple features:

1. **Release Manager** - Find releases containing only Bug issues
2. **Initiative Exporter** - Export Initiatives to JSON file

## Features

### Release Manager

- ✅ Lists releases that contain only "Bug" or "Customer bug" issue types
- ✅ Auto-discovers "Investment Category" custom field
- 🔜 Updates the "Investment Category" custom field for matching Release issues (Phase 2)

### Initiative Exporter

- ✅ Exports Initiative issues to JSON file
- ✅ Filters by status (excludes DONE and CANCELED)
- ✅ Includes issue key, description, requester, and linked issues count
- ✅ Generates timestamped JSON files

## Technology

- **Pure REST API**: Uses Jira Cloud REST API v3 directly (no external Jira libraries)
- **Python 3.x**: Modern Python with type hints
- **Requests library**: For HTTP communication
- **Environment variables**: Secure credential management

## Setup

1. **Create a virtual environment:**

   ```powershell
   python -m venv venv
   ```

2. **Activate the virtual environment:**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Create a `.env` file from the example:**

   ```powershell
   Copy-Item .env.example .env
   ```

5. **Update `.env` with your Jira credentials:**

   - `JIRA_URL`: Your Jira Cloud instance URL (e.g., `https://yourcompany.atlassian.net`)
   - `JIRA_EMAIL`: Your Jira email address
   - `JIRA_API_TOKEN`: Your Jira API token

   **Generate API Token:** Visit https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

Run the main script to access all features:

```powershell
python sources/jira_tool.py
```

### Main Menu

The script presents a menu with the following options:

1. **Release Manager** - Find releases with only Bug issues
2. **Initiative Exporter** - Export Initiatives to JSON
3. **Exit** - Quit the application

### Release Manager Flow

1. Optionally lists all available projects
2. Prompts for project key
3. Searches for "Investment Category" custom field
4. Analyzes all releases in the project
5. Lists releases containing only "Bug" or "Customer bug" issues

### Initiative Exporter Flow

1. Optionally lists all available projects
2. Prompts for project key
3. Fetches all Initiative issues (not DONE or CANCELED)
4. Exports to JSON file with:
   - Issue key
   - Description
   - Requester (reporter)
   - Number of linked issues
5. Saves to timestamped file: `initiatives_{PROJECT}_{TIMESTAMP}.json`

## Project Structure

```
InvestmentCategories/
├── sources/                  # Python source files
│   ├── jira_tool.py          # Main entry point with menu
│   ├── jira_client.py        # Jira REST API v3 client
│   ├── release_manager.py    # Release management features
│   └── initiative_exporter.py # Initiative export functionality
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .env.example              # Example environment template
├── .gitignore               # Git ignore patterns
├── README.md                # This file
└── .github/
    └── copilot-instructions.md  # Project documentation
```

## API Endpoints Used

The tool uses the following Jira Cloud REST API v3 endpoints:

### Common

- `GET /rest/api/3/project` - List all projects (used for connection test and project list)

### Release Manager

- `GET /rest/api/3/field` - Get all fields (including custom fields)
- `GET /rest/api/3/project/{projectKey}/versions` - Get project releases
- `POST /rest/api/3/search/jql` - Search issues with JQL
- `GET /rest/api/3/issue/{issueKey}/editmeta` - Get issue edit metadata

### Initiative Exporter

- `POST /rest/api/3/search/jql` - Search for Initiative issues with status filter

## Development

### Dependencies

- `requests==2.32.3` - HTTP library for REST API calls
- `python-dotenv==1.0.0` - Environment variable management

### Code Structure

- **JiraClient class**: Simple REST API wrapper with GET/POST/PUT methods
- **connect_to_jira()**: Establishes authenticated connection
- **get_all_projects()**: Lists available projects
- **get_investment_category_field_id()**: Finds custom field ID
- **get_all_releases()**: Retrieves project releases
- **get_issues_in_release()**: Gets issues for a specific release
- **check_release_has_only_bugs()**: Validates issue types in release
- **find_qualifying_releases()**: Main analysis logic

## Next Steps (Phase 2)

- Add functionality to update "Investment Category" field
- Find corresponding Release issues by version number
- Update field to "Product Growth (Offense)"
- Add dry-run mode for safety
- Add logging and reporting
