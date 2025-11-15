"""
FastMCP MotherDuck Server with Read Scaling

A high-performance MCP server for querying MotherDuck.
Each instance connects to one random read replica.
FastMCP Cloud handles horizontal scaling across instances.
"""

import os
import random
import logging
import threading
from typing import Optional
import duckdb
from tabulate import tabulate
from fastmcp import FastMCP

# Configuration from environment variables
DB_PATH = os.getenv("DB_PATH", "md:antm_hack")
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
READ_SCALING_REPLICAS = int(os.getenv("READ_SCALING_REPLICAS", "16"))
SESSION_HINT_RANGE = int(os.getenv("SESSION_HINT_RANGE", "100"))
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
    """Initialize connection to a random read replica"""
    global _conn, _replica_id
    
    if _conn:
        return  # Already initialized
    
    # Pick a random session hint (wider range than actual replicas for better distribution)
    _replica_id = random.randint(1, SESSION_HINT_RANGE)
    
    # Build connection string with token and session hint
    if MOTHERDUCK_TOKEN:
        separator = "&" if "?" in DB_PATH else "?"
        connection_path = f"{DB_PATH}{separator}motherduck_token={MOTHERDUCK_TOKEN}&session_hint={_replica_id}"
    else:
        separator = "&" if "?" in DB_PATH else "?"
        connection_path = f"{DB_PATH}{separator}session_hint={_replica_id}"
    
    _conn = duckdb.connect(connection_path, read_only=True)
    logger.info(f"🦆 Connected to MotherDuck with session_hint={_replica_id} ({READ_SCALING_REPLICAS} replicas available)")


def execute_query(query: str, params: Optional[list] = None) -> str:
    """Execute a query and return formatted results"""
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
        headers = [d[0] + "\n" + str(d[1]) for d in result.description]
        
        # Format as table
        output = tabulate(rows, headers=headers, tablefmt="pretty")
        
        # Apply character limit
        char_truncated = len(output) > MAX_CHARS
        if char_truncated:
            output = output[:MAX_CHARS]
        
        # Add warnings
        if has_more_rows:
            output += f"\n\n⚠️  Showing first {len(rows)} rows."
        elif char_truncated:
            output += f"\n\n⚠️  Output truncated at {MAX_CHARS:,} characters."
        
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
        Formatted table with query results
    """
    return execute_query(query)


@mcp.tool()
def show_tables(database_name: str) -> str:
    """
    Show all tables in a specific database.
    
    Args:
        database_name: Name of the database to list tables from
    
    Returns:
        Formatted table with database tables
    """
    return execute_query(
        "SELECT * FROM duckdb_tables() WHERE database_name = ?",
        [database_name]
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
logger.info(f"  • Database: {DB_PATH}")
logger.info(f"  • Read replicas: {READ_SCALING_REPLICAS}")
logger.info(f"  • Session hint: {_replica_id} (range: 1-{SESSION_HINT_RANGE})")
logger.info(f"  • Query timeout: {QUERY_TIMEOUT}s")
logger.info(f"  • Max rows: {MAX_ROWS}")
logger.info(f"  • Max chars: {MAX_CHARS:,}")
