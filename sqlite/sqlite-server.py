from mcp.server.fastmcp import FastMCP
import sqlite3
import os

mcp = FastMCP("Community Chatter")

# Define a tool to fetch data from SQLite database
@mcp.tool()
def fetch_data_from_db(q):
    """Fetch data from SQLite database based on the query."""
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("community.db")
    cursor = conn.cursor()

    # Execute the query to fetch data safely
    cursor.execute("SELECT name, messages FROM chatters ORDER BY messages DESC")
    results = cursor.fetchall()
    conn.close()

    # Format the results as a list of dictionaries
    formatted_results = [{"name": name, "messages": messages} for name, messages in results]
    return formatted_results

    # Run the MCP server locally
if __name__ == "__main__":
    mcp.run()