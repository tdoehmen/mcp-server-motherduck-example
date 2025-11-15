# MotherDuck MCP Server for ANTM Hackathon

FastMCP server for querying the ANTM hackathon dataset in MotherDuck with read scaling support.

## What is This?

This MCP server gives AI assistants (Claude, ChatGPT, etc.) direct access to the [America's Next Top Modeler](https://github.com/TheoryVentures/antm) hackathon dataset via SQL queries. The data is hosted in MotherDuck's `antm_hack` database.

## Features

- **Query Tool**: Execute SQL queries on the hackathon dataset
- **Show Tables Tool**: List all tables in the database  
- **Get Guide Tool**: DuckDB SQL syntax reference and performance tips
- **SaaS Mode**: Enhanced security (read-only, restricted file/database access)
- **Read Scaling**: Horizontal scaling with connection pooling
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

5. **Deploy!**

[FastMCP Cloud](https://fastmcp.cloud) will auto-detect `motherduck_server.py` and deploy it.

### Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MOTHERDUCK_TOKEN="your_token_here"
export USE_READ_SCALING=true

# Run the server
fastmcp run motherduck_server.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MOTHERDUCK_TOKEN` | ✅ Yes | - | Your MotherDuck token (regular or read scaling) |
| `USE_READ_SCALING` | No | false | Enable read scaling with session hints |
| `MAX_ROWS` | No | 1024 | Maximum rows in query results |
| `MAX_CHARS` | No | 50000 | Maximum characters in output |
| `QUERY_TIMEOUT` | No | 120 | Query timeout in seconds |

## Available Tools

### `query`
Execute any SQL query on the dataset.

**Example:**
```sql
SELECT * FROM customers LIMIT 10
```

### `show_tables`  
List all tables in a specific database.

**Example:**
```python
show_tables("antm_hack")
```

### `get_guide`
Get DuckDB SQL syntax and performance guide.

## The Dataset

The hackathon includes:
- **24 Parquet tables**: Structured retail data
- **19 JSONL log files**: Event streams  
- **Multiple PDFs**: Contracts, invoices, policies

Access it all via SQL queries to MotherDuck.

## Scaling Architecture

[FastMCP Cloud](https://fastmcp.cloud) autoscales and load balances traffic across multiple server instances based on demand. 

MotherDuck [read scaling tokens](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/read-scaling/) provide multiple read-only replicas of your database for improved concurrent query performance.

When `USE_READ_SCALING=true`, each server instance:
- Connects to one MotherDuck read replica
- Maintains that connection for its lifetime

This distributes load across both FastMCP instances and MotherDuck read replicas for optimal performance. 

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
