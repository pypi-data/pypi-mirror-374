import requests
import urllib3
import json
from typing import Any, Dict, List, Union

class DatabaseExistsError(Exception):
    """Custom exception raised when a database already has an admin key."""
    pass

class XplainDBClient:
    """
    A Python client for interacting with an XplainDB server.
    
    It is recommended to create a client instance using the create_db() classmethod 
    or by providing an existing API key.
    
    Args:
        base_url (str): The base URL of the XplainDB server (e.g., 'https://api.xplaindb.com').
        db_name (str): The name of the database to connect to.
        api_key (str): The API key for authentication.
        verify_ssl (bool): Set to False to disable SSL certificate verification. Defaults to True.
    """
    def __init__(self, base_url: str, db_name: str, api_key: str, verify_ssl: bool = True):
        if not all([base_url, db_name, api_key]):
            raise ValueError("Base URL, DB name, and API key are all required.")
        
        self.base_url = base_url.rstrip('/')
        self.db_name = db_name
        self.api_key = api_key
        self._rest_url = f"{self.base_url}/{self.db_name}/query"
        self._graphql_url = f"{self.base_url}/{self.db_name}/graphql"
        
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._session = requests.Session()
        self._session.verify = verify_ssl
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        })

    @classmethod
    def create_db(cls, base_url: str, db_name: str, verify_ssl: bool = True) -> 'XplainDBClient':
        """
        Connects to an XplainDB database. If new, it's created and its admin key is retrieved.
        If it already exists, raises DatabaseExistsError.

        Returns:
            An authenticated XplainDBClient instance.
        """
        print(f"--- Bootstrapping database '{db_name}'...")
        bootstrap_url = f"{base_url.rstrip('/')}/{db_name}/bootstrap"
        
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        try:
            response = requests.get(bootstrap_url, timeout=10, verify=verify_ssl)
            if response.status_code == 403:
                raise DatabaseExistsError(f"Database '{db_name}' already exists and is bootstrapped. Initialize the client directly with its API key.")
            
            response.raise_for_status()
            key = response.json().get("admin_key")
            if not key:
                raise ValueError("Admin key not found in bootstrap response.")
            
            print("✅ Success: Retrieved new admin key.")
            return cls(base_url=base_url, db_name=db_name, api_key=key, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to the XplainDB server at {base_url}. Is it running?") from e

    def _make_request(self, payload: Dict[str, Any], endpoint_url: str) -> Dict[str, Any]:
        """Internal helper to make authenticated requests."""
        try:
            response = self._session.post(endpoint_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            detail = e.response.json().get("detail", e.response.text)
            raise ConnectionError(f"API Error ({e.response.status_code}): {detail}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network request failed: {e}") from e

    def sql(self, query: str) -> List[Dict[str, Any]]:
        """Executes a raw SQL query."""
        response = self._make_request({"query": query}, self._rest_url)
        return response.get("result", [])

    def command(self, cmd_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes a dictionary-based command (document, graph, vector, etc.)."""
        response = self._make_request({"query": cmd_dict}, self._rest_url)
        return response.get("result", [])

    def create_view(self, view_name: str, collection: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Creates a writable SQL view for a collection."""
        view_command = {
            "type": "create_view",
            "view_name": view_name,
            "collection": collection,
            "fields": fields
        }
        return self.command(view_command)

    def create_api_key(self, permissions: str = "reader") -> Dict[str, str]:
        """Creates a new API key (requires admin privileges)."""
        if permissions not in ['reader', 'writer', 'admin']:
            raise ValueError("Permissions must be 'reader', 'writer', or 'admin'.")
            
        key_command = {"type": "create_key", "permissions": permissions}
        result = self.command(key_command)
        return result[0] if result else {}

    def graphql(self, query: str) -> Dict[str, Any]:
        """
        Executes a GraphQL query. 
        The query can be a standard GraphQL query string or a JSON-escaped dictionary command.
        """
        # For dictionary commands, we need to escape them into a valid JSON string
        if not query.strip().startswith("query"):
            query = json.dumps(query)

        graphql_payload = {"query": f'query {{ execute(query: {json.dumps(query)}) {{ data status }} }}'}
        response_data = self._make_request(graphql_payload, self._graphql_url).get("data", {})

        if 'execute' in response_data and 'data' in response_data['execute']:
             response_data['execute']['data'] = json.loads(response_data['execute']['data'])
        return response_data
