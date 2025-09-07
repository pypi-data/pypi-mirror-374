import requests
import urllib3
import json
from typing import Any, Dict, List, Optional

# --- Custom Exception ---
class DatabaseExistsError(Exception):
    """Custom exception raised when a database already has an admin key."""
    pass

# ==============================================================================
# XplainDBClient Class
# ==============================================================================

class XplainDBClient:
    """
    A Python client for interacting with an XplainDB v3.0.0 server.
    
    It is recommended to create a client instance using the create_db() classmethod 
    or by providing an existing API key.
    
    Args:
        base_url (str): The base URL of the XplainDB server.
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
        Connects to a new XplainDB database, creates it, and retrieves its admin key.
        If the database already exists, raises DatabaseExistsError.

        Returns:
            An authenticated XplainDBClient instance for the new database.
        """
        print(f"--- Bootstrapping new database '{db_name}'...")
        bootstrap_url = f"{base_url.rstrip('/')}/{db_name}/bootstrap"
        
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        try:
            response = requests.get(bootstrap_url, timeout=10, verify=verify_ssl)
            if response.status_code == 403:
                raise DatabaseExistsError(f"Database '{db_name}' already exists. Initialize the client directly with its API key.")
            
            response.raise_for_status()
            key = response.json().get("admin_key")
            if not key:
                raise ValueError("Admin key not found in bootstrap response.")
            
            print(f"✅ Success: Retrieved new admin key for '{db_name}'.")
            return cls(base_url=base_url, db_name=db_name, api_key=key, verify_ssl=verify_ssl)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not connect to the XplainDB server at {base_url}.") from e

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to make authenticated requests."""
        try:
            response = self._session.post(self._rest_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            detail = e.response.json().get("detail", e.response.text)
            raise ConnectionError(f"API Error ({e.response.status_code}): {detail}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network request failed: {e}") from e

    # --- Low-Level API ---
    def command(self, cmd_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes a raw dictionary-based command (document, graph, vector, etc.)."""
        response = self._make_request({"query": cmd_dict})
        return response.get("result", [])

    def sql(self, query: str) -> List[Dict[str, Any]]:
        """Executes a raw SQL query."""
        response = self._make_request({"query": query})
        return response.get("result", [])

    # --- Document API ---
    def document_insert(self, collection: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Inserts a single document into a collection."""
        cmd = {"type": "insert", "collection": collection, "data": data}
        return self.command(cmd)
    
    def document_search(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Searches for documents in a collection matching a query."""
        cmd = {"type": "search", "collection": collection, "query": query}
        return self.command(cmd)

    def document_update(self, collection: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Updates documents matching a query using a $set operation."""
        cmd = {"type": "update", "collection": collection, "query": query, "update": {"$set": update_data}}
        return self.command(cmd)
        
    def document_delete(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Deletes documents from a collection matching a query."""
        cmd = {"type": "delete", "collection": collection, "query": query}
        return self.command(cmd)

    # --- Graph API ---
    def graph_add_edge(self, source: str, target: str, label: str, properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Creates a directed edge from a source document to a target document."""
        cmd = {"type": "add_edge", "source": source, "target": target, "label": label, "properties": properties or {}}
        return self.command(cmd)

    def graph_get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """Retrieves the direct neighbors of a document (node)."""
        cmd = {"type": "get_neighbors", "node_id": node_id}
        return self.command(cmd)

    # --- Vector API ---
    def vector_embed_and_add(self, text_field: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embeds and adds a list of documents to the vector index."""
        cmd = {"type": "embed_and_add", "text_field": text_field, "documents": documents}
        return self.command(cmd)

    def vector_find_similar(self, query_text: str, k: int, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Performs a semantic search with an optional metadata filter."""
        cmd = {"type": "find_similar", "query_text": query_text, "k": k, "filter": filter}
        return self.command(cmd)

    # --- Admin & Schema API ---
    def register_vector_field(self, collection: str, text_field: str) -> List[Dict[str, Any]]:
        """Registers a field in a collection for automatic vectorization on update."""
        cmd = {"type": "register_vector_field", "collection": collection, "text_field": text_field}
        return self.command(cmd)

    def create_view(self, view_name: str, collection: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Creates a writable SQL view for a collection."""
        cmd = {"type": "create_view", "view_name": view_name, "collection": collection, "fields": fields}
        return self.command(cmd)

    def create_api_key(self, permissions: str = "reader") -> Dict[str, str]:
        """Creates a new API key (requires admin privileges)."""
        if permissions not in ['reader', 'writer', 'admin']:
            raise ValueError("Permissions must be 'reader', 'writer', or 'admin'.")
        
        cmd = {"type": "create_key", "permissions": permissions}
        result = self.command(cmd)
        return result[0] if result else {}