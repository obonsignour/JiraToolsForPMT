"""
Jira Client - Simple REST API v3 wrapper

This module provides a lightweight client for interacting with Jira Cloud REST API v3.
Uses requests library with session-based authentication.
"""

import os
from typing import Dict, Optional
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


class JiraClient:
    """Simple Jira Cloud REST API v3 client."""
    
    def __init__(self, url: str, email: str, api_token: str):
        """
        Initialize Jira client.
        
        Args:
            url: Jira instance URL (e.g., https://yourcompany.atlassian.net)
            email: Jira user email
            api_token: Jira API token
        """
        self.base_url = url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a GET request to Jira API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make a POST request to Jira API.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Optional JSON data
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        if not response.ok:
            # Debug: print response for troubleshooting
            try:
                error_detail = response.json()
                print(f"API Error Response: {error_detail}")
            except:
                print(f"API Error Response: {response.text}")
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make a PUT request to Jira API.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Optional JSON data
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()
    
    @classmethod
    def from_env(cls) -> 'JiraClient':
        """
        Create a JiraClient instance from environment variables.
        
        Loads credentials from .env file and establishes a connection to Jira.
        Tests the connection by fetching the list of accessible projects.
        
        Environment variables required:
            JIRA_URL: Jira instance URL (e.g., https://yourcompany.atlassian.net)
            JIRA_EMAIL: Jira user email
            JIRA_API_TOKEN: Jira API token
        
        Returns:
            JiraClient: Authenticated and tested Jira client instance
            
        Raises:
            ValueError: If environment variables are missing or authentication fails
        """
        load_dotenv()
        
        jira_url = os.getenv('JIRA_URL')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_token = os.getenv('JIRA_API_TOKEN')
        
        if not all([jira_url, jira_email, jira_api_token]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

        # Clean up URL
        jira_url = jira_url.strip().rstrip('/')
        
        client = cls(jira_url, jira_email, jira_api_token)
        
        # Test connection by getting list of projects (works with scoped tokens)
        try:
            # Simple GET request to test authentication
            result = client.get('rest/api/3/project')
            print(f"✓ Connected to Jira: {jira_url} (REST API v3)")
            print(f"✓ Authentication successful (scoped token)")
            if isinstance(result, list) and len(result) > 0:
                print(f"✓ Access to {len(result)} project(s)")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"\n❌ 401 Unauthorized Error")
                print(f"   This usually means:")
                print(f"   1. Your API token is incorrect or expired")
                print(f"   2. Your email doesn't match the Jira account")
                print(f"   3. Your API token doesn't have the right scopes")
                print(f"\n   Please verify:")
                print(f"   - Your .env file exists and has the correct values")
                print(f"   - Your API token is valid (generate new at: https://id.atlassian.com/manage-profile/security/api-tokens)")
                print(f"   - Your JIRA_EMAIL matches your Atlassian account email")
                print(f"   - Your API token has 'Read' scope for Jira")
                raise ValueError("Authentication failed. Please check your JIRA_EMAIL and JIRA_API_TOKEN in .env file.")
            else:
                raise ValueError(f"Failed to connect to Jira: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to connect to Jira: {str(e)}")
        
        return client
