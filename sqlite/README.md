# SQLite MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with SQLite databases. This server enables AI assistants to query, manage, and analyze SQLite databases through a standardized interface.

## Features

- **Database Operations**: Execute SQL queries, create tables, insert data, and more
- **Schema Inspection**: View database schema, table structures, and relationships
- **Data Analysis**: Query and analyze data stored in SQLite databases
- **Safe Execution**: Read-only and read-write modes for security
- **Multiple Database Support**: Connect to multiple SQLite databases simultaneously

## Table of Contents

- [Installation](#installation)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

```bash
# Navigate to the sqlite directory
cd mcp-server/sqlite

# Create virtual environment
python -m venv mcp-env

# Activate virtual environment
# On macOS/Linux:
source mcp-env/bin/activate
# On Windows:
mcp-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Setup

### 1. Install Dependencies

Ensure your `requirements.txt` includes:

```txt
mcp>=0.1.0
```

Install:
```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python sqlite-server.py
```

### 3. Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-server/sqlite/sqlite-server.py"],
      "env": {
        "DATABASE_PATH": "/absolute/path/to/mcp-server/sqlite/community.db"
      }
    }
  }
}
```

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "/Users/yourname/mcp-server/sqlite/mcp-env/bin/python",
      "args": ["/Users/yourname/mcp-server/sqlite/sqlite-server.py"],
      "env": {
        "DATABASE_PATH": "/Users/yourname/mcp-server/sqlite/community.db"
      }
    }
  }
}
```

**Windows Example:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "C:\\Users\\yourname\\mcp-server\\sqlite\\mcp-env\\Scripts\\python.exe",
      "args": ["C:\\Users\\yourname\\mcp-server\\sqlite\\sqlite-server.py"],
      "env": {
        "DATABASE_PATH": "C:\\Users\\yourname\\mcp-server\\sqlite\\community.db"
      }
    }
  }
}
```

## Configuration

### Environment Variables

- `DATABASE_PATH`: Path to the SQLite database file (default: `./community.db`)
- `READ_ONLY`: Set to `true` for read-only access (default: `false`)
- `MAX_RESULTS`: Maximum number of rows to return from queries (default: `1000`)

### Example Configuration

Create a `.env` file (optional):

```bash
DATABASE_PATH=/path/to/community.db
READ_ONLY=false
MAX_RESULTS=500
```

## Usage

### Basic Workflow

1. **Start the server**: The MCP server runs in the background
2. **Connect your client**: Use Claude Desktop or another MCP-compatible client
3. **Execute tools**: Use natural language to interact with your database

### Sample Interactions

```
User: "Show me all tables in the database"
Assistant: [Uses list_tables tool]

User: "What's the schema for the users table?"
Assistant: [Uses describe_table tool]

User: "Find all users who signed up in the last 30 days"
Assistant: [Uses query_database tool with appropriate SQL]
```

## Available Tools

### 1. `query_database`
Execute SQL queries on the database.

**Parameters:**
- `query` (string, required): SQL query to execute
- `params` (array, optional): Parameters for parameterized queries

**Example:**
```json
{
  "query": "SELECT * FROM users WHERE age > ?",
  "params": [25]
}
```

### 2. `list_tables`
List all tables in the database.

**Parameters:** None

**Returns:** Array of table names

### 3. `describe_table`
Get the schema/structure of a specific table.

**Parameters:**
- `table_name` (string, required): Name of the table

**Returns:** Table schema including column names, types, and constraints

### 4. `create_table`
Create a new table in the database.

**Parameters:**
- `table_name` (string, required): Name of the new table
- `schema` (string, required): SQL schema definition

**Example:**
```json
{
  "table_name": "products",
  "schema": "id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL"
}
```

### 5. `insert_data`
Insert data into a table.

**Parameters:**
- `table_name` (string, required): Target table name
- `data` (object, required): Key-value pairs of column names and values

**Example:**
```json
{
  "table_name": "products",
  "data": {
    "name": "Widget",
    "price": 19.99
  }
}
```

### 6. `execute_sql`
Execute arbitrary SQL statements (CREATE, UPDATE, DELETE, etc.).

**Parameters:**
- `sql` (string, required): SQL statement to execute
- `params` (array, optional): Parameters for parameterized statements

**Example:**
```json
{
  "sql": "UPDATE products SET price = ? WHERE id = ?",
  "params": [24.99, 1]
}
```

### 7. `get_table_info`
Get detailed information about a table including row count and size.

**Parameters:**
- `table_name` (string, required): Name of the table

**Returns:** Table statistics and metadata

### 8. `backup_database`
Create a backup of the database.

**Parameters:**
- `backup_path` (string, required): Path where backup should be saved

**Returns:** Success message with backup location

## Examples

### Example 1: Creating and Populating a Database

```python
# Create a products table
create_table(
    table_name="products",
    schema="id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL, stock INTEGER DEFAULT 0"
)

# Insert sample data
insert_data(
    table_name="products",
    data={"name": "Laptop", "price": 999.99, "stock": 15}
)

insert_data(
    table_name="products",
    data={"name": "Mouse", "price": 29.99, "stock": 50}
)
```

### Example 2: Complex Query

```python
# Find products with low stock
query_database(
    query="SELECT name, stock FROM products WHERE stock < ? ORDER BY stock ASC",
    params=[20]
)
```

### Example 3: Database Analysis

```python
# Get table statistics
get_table_info(table_name="products")

# List all tables
list_tables()

# Describe table structure
describe_table(table_name="products")
```

## Security

### Best Practices

1. **Use Read-Only Mode**: For analysis and querying, enable read-only mode
   ```bash
   READ_ONLY=true python sqlite-server.py
   ```

2. **Parameterized Queries**: Always use parameterized queries to prevent SQL injection
   ```python
   # Good ✅
   query_database(query="SELECT * FROM users WHERE id = ?", params=[user_id])
   
   # Bad ❌
   query_database(query=f"SELECT * FROM users WHERE id = {user_id}")
   ```

3. **Limit Results**: Set `MAX_RESULTS` to prevent memory issues with large datasets

4. **Backup Regularly**: Use the `backup_database` tool before making schema changes

5. **Validate Inputs**: The server validates all inputs, but always verify data on the client side

### Database File Permissions

```bash
# Restrict database file access
chmod 600 community.db

# Make directory readable only by owner
chmod 700 /path/to/sqlite/
```

## Troubleshooting

### Common Issues

#### Database Locked Error
**Problem:** `database is locked` error when writing

**Solution:**
```bash
# Check for other processes using the database
lsof community.db

# Close other connections or use WAL mode
query_database(query="PRAGMA journal_mode=WAL")
```

#### Permission Denied
**Problem:** Cannot read/write database file

**Solution:**
```bash
# Check file permissions
ls -l community.db

# Fix permissions
chmod 644 community.db
```

#### Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
# Ensure virtual environment is activated
source mcp-env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Large Query Results
**Problem:** Queries return too much data

**Solution:**
```python
# Use LIMIT clause
query_database(query="SELECT * FROM large_table LIMIT 100")

# Or adjust MAX_RESULTS environment variable
```

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
python sqlite-server.py
```

### Getting Help

- Check the [MCP Documentation](https://modelcontextprotocol.io/docs)
- Review SQLite [official documentation](https://www.sqlite.org/docs.html)
- Open an issue on [GitHub](https://github.com/YOUR_USERNAME/mcp-server/issues)

## Performance Tips

1. **Create Indexes**: For frequently queried columns
   ```sql
   CREATE INDEX idx_user_email ON users(email);
   ```

2. **Use ANALYZE**: Keep query optimizer statistics updated
   ```sql
   ANALYZE;
   ```

3. **Enable WAL Mode**: For better concurrency
   ```sql
   PRAGMA journal_mode=WAL;
   ```

4. **Vacuum Regularly**: Reclaim unused space
   ```sql
   VACUUM;
   ```

## Project Structure

```
sqlite/
├── README.md              # This file
├── sqlite-server.py       # Main MCP server
├── requirements.txt       # Python dependencies
├── community.db          # SQLite database file
├── mcp-env/              # Virtual environment (not in git)
└── .gitignore            # Git ignore rules
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/mcp-server.git
cd mcp-server/sqlite
python -m venv mcp-env
source mcp-env/bin/activate
pip install -r requirements.txt

# Run tests
pytest

# Run linter
flake8 sqlite-server.py

# Format code
black sqlite-server.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io)
- Powered by [SQLite](https://www.sqlite.org/)
- Inspired by the MCP community

## Changelog

### Version 1.0.0 (2024-10-03)
- Initial release
- Basic CRUD operations
- Schema inspection tools
- Backup functionality
- Support for community.db database

---

**Need help?** Open an issue or check the [troubleshooting section](#troubleshooting).

**Want to contribute?** See our [contributing guidelines](#contributing).