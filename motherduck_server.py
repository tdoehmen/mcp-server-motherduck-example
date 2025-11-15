"""
FastMCP MotherDuck Server

A high-performance MCP server for querying MotherDuck.
Each instance uses a random session hint for optimal load distribution.
Supports both regular tokens and read scaling tokens.
FastMCP Cloud handles horizontal scaling across instances.
"""

import os
import random
import logging
import threading
import json
from typing import Optional
import duckdb
from fastmcp import FastMCP

# Configuration from environment variables
DATABASE_NAME = os.getenv("DATABASE_NAME", "antm_hack")
DB_PATH = f"md:{DATABASE_NAME}"
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
MAX_ROWS = int(os.getenv("MAX_ROWS", "1024"))
MAX_CHARS = int(os.getenv("MAX_CHARS", "50000"))
QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "120"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("motherduck_mcp")

# Create FastMCP server
mcp = FastMCP("MotherDuck")

# Single connection for this instance
_conn: Optional[duckdb.DuckDBPyConnection] = None
_replica_id: Optional[int] = None


def initialize_connection():
    """Initialize connection to MotherDuck"""
    global _conn, _replica_id
    
    if _conn:
        return  # Already initialized
    
    # Require MotherDuck token
    if not MOTHERDUCK_TOKEN:
        raise ValueError("MOTHERDUCK_TOKEN environment variable is required")
    
    # Always use session_hint for load distribution (harmless no-op with regular tokens)
    _replica_id = random.randint(1, 1000)
    
    # Build connection parameters (saas_mode and session_hint must be in path)
    params = ["saas_mode=true", f"session_hint={_replica_id}"]
    
    # Build connection string
    connection_path = f"{DB_PATH}?{'&'.join(params)}"
    
    # Connect with token in config
    _conn = duckdb.connect(
        connection_path,
        read_only=True,
        config={'motherduck_token': MOTHERDUCK_TOKEN}
    )
    
    logger.info(f"🦆 Connected to MotherDuck in SaaS mode (session_hint={_replica_id})")


def execute_query(query: str, params: Optional[list] = None) -> str:
    """Execute a query and return results as JSON"""
    if not _conn:
        initialize_connection()
    
    # Set up timeout if configured
    timer = None
    if QUERY_TIMEOUT > 0:
        timer = threading.Timer(QUERY_TIMEOUT, _conn.interrupt)
        timer.start()
    
    try:
        # Execute query with or without parameters
        if params:
            result = _conn.execute(query, params)
        else:
            result = _conn.execute(query)
        
        # Fetch results
        rows = result.fetchmany(MAX_ROWS)
        has_more_rows = result.fetchone() is not None
        column_names = [d[0] for d in result.description]
        
        # Convert to list of dictionaries
        data = [dict(zip(column_names, row)) for row in rows]
        
        # Build response object
        response = {
            "data": data,
            "row_count": len(data),
            "truncated": has_more_rows
        }
        
        # Add truncation warning if needed
        if has_more_rows:
            response["warning"] = f"Results limited to {MAX_ROWS} rows"
        
        # Convert to JSON string
        output = json.dumps(response, indent=2, default=str)
        
        # Apply character limit
        if len(output) > MAX_CHARS:
            output = output[:MAX_CHARS]
            output += f'\n\n"warning": "Output truncated at {MAX_CHARS:,} characters"'
        
        return output
    
    except duckdb.InterruptException:
        raise ValueError(f"❌ Query execution timed out after {QUERY_TIMEOUT} seconds")
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise ValueError(f"❌ Error executing query: {e}")
    finally:
        if timer:
            timer.cancel()


@mcp.tool()
def query(query: str) -> str:
    """
    Execute a SQL query on the MotherDuck database.
    
    Args:
        query: SQL query to execute (DuckDB SQL dialect)
    
    Returns:
        JSON with query results (data, row_count, truncated)
    """
    return execute_query(query)


@mcp.tool()
def show_tables() -> str:
    """
    Show all tables in the database.
    
    Returns:
        JSON with all tables in the configured database
    """
    return execute_query(
        "SELECT * FROM duckdb_tables() WHERE database_name = ?",
        [DATABASE_NAME]
    )


@mcp.tool()
def get_guide() -> str:
    """
    Get the DuckDB SQL query syntax and performance guide.
    
    Returns:
        Complete guide with tips and best practices
    """
    try:
        import pathlib
        guide_path = pathlib.Path(__file__).parent / "src" / "mcp_server_motherduck" / "query_guide.md"
        
        if not guide_path.exists():
            # Try alternative path
            guide_path = pathlib.Path(__file__).parent / "query_guide.md"
        
        if guide_path.exists():
            return guide_path.read_text(encoding="utf-8")
        else:
            return "❌ Error: Query guide file not found"
    except Exception as e:
        return f"❌ Error reading guide: {str(e)}"


# Initialize connection on module load
initialize_connection()
logger.info("🚀 MotherDuck MCP Server ready!")
logger.info(f"📊 Configuration:")
logger.info(f"  • Database: {DATABASE_NAME}")
logger.info(f"  • Session hint: {_replica_id}")
logger.info(f"  • Query timeout: {QUERY_TIMEOUT}s")
logger.info(f"  • Max rows: {MAX_ROWS}")
logger.info(f"  • Max chars: {MAX_CHARS:,}")
