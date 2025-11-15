# MotherDuck MCP Server on FastMCP Cloud

FastMCP server for querying the ANTM hackathon dataset in MotherDuck with read scaling support.

## What is This?

This MCP server gives AI assistants (Claude, ChatGPT, etc.) direct access to the [America's Next Top Modeler](https://github.com/TheoryVentures/antm) hackathon dataset via a remote MotherDuck MCP server, hosted on FastMCP Cloud.

## Features

- **Query Tool**: Execute SQL queries on the hackathon dataset
- **Show Tables Tool**: List all tables in the configured database  
- **Get Guide Tool**: DuckDB SQL syntax reference and performance tips
- **Read Only**: Connections established in [read-only mode](https://motherduck.com/docs/key-tasks/ai-and-motherduck/building-analytics-agents/#read-only-access) and in [SaaS mode](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#authentication-using-saas-mode) to restrict local file/database access within the remote MCP server
- **Autoscaling**: FastMCP Cloud and MotherDuck read scaling (see [Autoscaling](#autoscaling) section)
- **Query Timeout**: 120 second timeout protection
- **Result Limits**: Max 1024 rows, 50,000 characters

## Quick Start

### Deploy to FastMCP Cloud

1. **Push to GitHub** (if not already done)

2. **Go to [FastMCP Cloud](https://fastmcp.cloud)**

3. **Connect your repository**

4. **Set environment variable**:
   ```
   MOTHERDUCK_TOKEN=<your_read_scaling_token>
   ```
   (Read scaling is enabled by default)

5. **Deploy!**

[FastMCP Cloud](https://fastmcp.cloud) will auto-detect `motherduck_server.py` and deploy it.

### Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export MOTHERDUCK_TOKEN="your_read_scaling_token_here"

# Run the server (read scaling enabled by default)
fastmcp run motherduck_server.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MOTHERDUCK_TOKEN` | ✅ Yes | - | Your MotherDuck token (use read scaling token) |
| `DATABASE_NAME` | No | antm_hack | Name of the MotherDuck database to connect to |
| `USE_READ_SCALING` | No | true | Set to `false` to disable read scaling and use regular MotherDuck token |
| `MAX_ROWS` | No | 1024 | Maximum rows in query results |
| `MAX_CHARS` | No | 50000 | Maximum characters in output |
| `QUERY_TIMEOUT` | No | 120 | Query timeout in seconds |

## Available Tools

### `query`
Execute any SQL query on the dataset.

**Returns:** JSON with `data` (array of row objects), `row_count`, and `truncated` flag.

**Example:**
```sql
SELECT * FROM customers LIMIT 10
```

### `show_tables`  
List all tables in the database (uses configured `DATABASE_NAME`).

**Returns:** JSON with table information.

**No parameters needed.**

### `get_guide`
Get DuckDB SQL syntax guide.

## The Dataset

The hackathon includes:
- **24 Parquet tables**: Structured retail data
- **19 JSONL log files**: Event streams  
- **Multiple PDFs**: Contracts, invoices, policies

Access it all via SQL queries to MotherDuck.

## Autoscaling

[FastMCP Cloud](https://fastmcp.cloud) autoscales and load balances traffic across multiple server instances based on demand. 

[MotherDuck read scaling tokens](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/read-scaling/) provide multiple read-only replicas of your database for improved concurrent query performance.

With read-scaling enabled default, each server instance:
- Picks a random session hint on startup
- Connects to one MotherDuck read replica
- Maintains that connection for its lifetime

This distributes load across both FastMCP instances and MotherDuck read replicas for optimal performance.

To disable read scaling and establish a connection with a regular MotherDuck token, set `USE_READ_SCALING=false`. 

## Links

- **Hackathon**: [github.com/TheoryVentures/antm](https://github.com/TheoryVentures/antm)
- **Competition Platform**: [hack.theoryvc.com](https://hack.theoryvc.com)
- **FastMCP**: [gofastmcp.com](https://gofastmcp.com/getting-started/welcome)
- **FastMCP Cloud**: [fastmcp.cloud](https://fastmcp.cloud)
- **MotherDuck**: [motherduck.com](https://motherduck.com)

## Files

```
.
├── motherduck_server.py    # Main FastMCP server
├── query_guide.md          # DuckDB SQL reference
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## License

MIT License

---

Built for [America's Next Top Modeler](https://github.com/TheoryVentures/antm) Hackathon by [Theory Ventures](https://theory.vc)
