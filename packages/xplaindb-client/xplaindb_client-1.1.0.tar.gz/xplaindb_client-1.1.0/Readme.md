

# XplainDB-Client - The Python Client for XplainDB

[](https://pypi.python.org/pypi/xplaindb-client)
[](https://www.python.org/downloads/)
[](https://www.gnu.org/licenses/lgpl-3.0)

**`xplaindb-client`** is the official Python client for **XplainDB**. It provides a simple, intuitive, and powerful interface for interacting with an XplainDB server, handling everything from database creation and security management to complex multi-model queries.

This client abstracts away the complexity of HTTP requests, allowing you to work with your **Document**, **Graph**, **Vector**, and **SQL** models using clean, Pythonic code on a single, unified data core.

-----

## Account Creation

Get your account created at [XplainDB](https://xplaindb.xplainnn.com/signup/) and in the [Dashboard](https://xplaindb.xplainnn.com/dashboard/), look for your **Tenant Domain**. This is your `BASE_URL`.

## Installation

Install the client library directly from PyPI.

```bash
pip install xplaindb-client
```

-----

## 📖 Getting Started: A Unified Walkthrough

This guide demonstrates how to model a simple application with "Users" and "Projects," showcasing how all data models work together.
### Step 0: Create an account at XplainDB:
Zeroth step is to create an account at [xplaindb](https://xplaindb.xplainnn.com/) and get the tenant url.

### Step 1: Connecting and Creating a Database

First, connect to the XplainDB server and bootstrap your database. `XplainDBClient.create_db()` handles this by creating the database (if new) and retrieving the root admin key.

```python
from xplaindb_client import XplainDBClient, DatabaseExistsError

# Configuration
BASE_URL = "https://your-tenant-domain.db.xplainnn.com"
DB_NAME = "project_tracker"

try:
    # This creates 'project_tracker' and gets the admin key.
    admin_client = XplainDBClient.create_db(
        base_url=BASE_URL, 
        db_name=DB_NAME,
        verify_ssl=True  # Set to False for local/dev servers with self-signed certs
    )
    print("✅ Successfully created database and connected as admin!")
    # In a real app, save this key securely.
    my_admin_key = admin_client.api_key
    print(f"Admin Key: {my_admin_key}")

except DatabaseExistsError:
    print(f"Database '{DB_NAME}' already exists. Connect using its API key.")
    # my_admin_key = "your_saved_admin_key"
    # admin_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=my_admin_key)
except ConnectionError as e:
    print(f"❌ Error: {e}")
```

### Step 2: Access Management (RBAC)

Use your `admin_client` to create less-privileged keys for different parts of your application.

```python
# Create a 'writer' key for your application's backend
writer_key_info = admin_client.create_api_key(permissions="writer")
writer_key = writer_key_info.get("api_key")
print(f"Created 'writer' key: {writer_key[:8]}...")

# Create a 'reader' key for an analytics dashboard or public-facing elements
reader_key_info = admin_client.create_api_key(permissions="reader")
reader_key = reader_key_info.get("api_key")
print(f"Created 'reader' key: {reader_key[:8]}...")

# Instantiate new clients that will act with these limited permissions
writer_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=writer_key)
reader_client = XplainDBClient(base_url=BASE_URL, db_name=DB_NAME, api_key=reader_key)
```

### Step 3: The Unified Core - Working with Documents

In XplainDB, everything starts as a flexible JSON document. Use the universal `.command()` method for all document operations.

```python
print("\n--- Document Operations ---")
# The writer can insert documents into collections
writer_client.command({
    "type": "insert",
    "collection": "users",
    "data": {"_id": "user_alice", "name": "Alice", "role": "Lead Engineer"}
})
writer_client.command({
    "type": "insert",
    "collection": "projects",
    "data": {"_id": "proj_phoenix", "name": "Project Phoenix", "status": "active"}
})
print("✅ Writer inserted a user and a project.")

# The reader can search for documents
active_projects = reader_client.command({
    "type": "search",
    "collection": "projects",
    "query": {"status": "active"}
})
print(f"  Reader found active projects: {active_projects}")
```

### Step 4: The Relational Lens - SQL & Writable Views

Bridge the gap between your NoSQL data and the power of SQL. Create a **writable view** to `SELECT`, `UPDATE`, and `INSERT` with familiar SQL syntax.

```python
print("\n--- SQL Operations ---")
# The admin creates a writable view, exposing JSON fields as SQL columns
admin_client.create_view(
    view_name="users_view",
    collection="users",
    fields=["_id", "name", "role"]
)
print("✅ Admin created a writable 'users_view'.")

# The writer can UPDATE data using a standard SQL command on the view
writer_client.sql("UPDATE users_view SET role = 'Principal Engineer' WHERE name = 'Alice'")
print("✅ Writer promoted Alice using SQL.")

# The reader can now SELECT the updated data from the view
engineers = reader_client.sql("SELECT name, role FROM users_view WHERE role LIKE '%Engineer'")
print(f"  Reader found engineers via SQL: {engineers}")

# Verify with a document search - the change is reflected everywhere!
alice_updated = reader_client.command({"type":"search", "collection":"users", "query":{"_id":"user_alice"}})
print(f"  NoSQL search confirms Alice's new role: {alice_updated[0]['role']}")
```

### Step 5: The Relationship Lens - Using the Graph

Model complex relationships by creating edges between your documents. The documents you inserted in Step 3 are already graph nodes.

```python
print("\n--- Graph Operations ---")
# The writer creates an edge to assign Alice to Project Phoenix
writer_client.command({
    "type": "add_edge",
    "source": "user_alice",
    "target": "proj_phoenix",
    "label": "WORKS_ON"
})
print("✅ Writer created a 'WORKS_ON' edge.")

# The reader can traverse the graph to find connections
alice_projects = reader_client.command({"type": "get_neighbors", "node_id": "user_alice"})
print(f"  Reader found Alice's projects via graph query: {alice_projects[0]['target_id']}")
```

### Step 6: The Semantic Lens - AI & Hybrid Vector Search

Enrich your documents with semantic meaning for powerful AI-driven queries.

```python
print("\n--- Vector Operations ---")
# First, update a document to include text for embedding
writer_client.command({
    "type":"update", "collection":"users", "query":{"_id":"user_alice"},
    "update":{"$set":{"bio":"Loves building scalable database systems."}}
})

# The writer tells the server to embed the 'bio' field for the existing document
writer_client.command({
    "type": "embed_and_add",
    "collection": "users",
    "text_field": "bio",
    "documents": [{"_id": "user_alice", "bio": "Loves building scalable database systems."}]
})
print("✅ Writer embedded Alice's bio.")

# The reader can now perform a HYBRID search:
# Find a "Principal Engineer" (NoSQL filter) whose bio is similar to "loves data" (Vector search)
hybrid_results = reader_client.command({
    "type": "find_similar",
    "collection": "users",
    "query_text": "loves data",
    "filter": {"role": "Principal Engineer"},
    "k": 1
})
print(f"  Reader ran a hybrid search and found: {hybrid_results[0]['document']['name']}")
```