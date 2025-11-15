# MotherDuck MCP Server on FastMCP Cloud

This MCP server gives AI assistants (Claude, ChatGPT, etc.) direct access to the [America's Next Top Modeler](https://github.com/TheoryVentures/antm) hackathon dataset via a remote [MotherDuck](https://motherduck.com) MCP server, hosted on [FastMCP Cloud](https://fastmcp.cloud).

## Features

- **Query Tool**: Execute SQL queries on the hackathon dataset
- **Show Tables Tool**: List all tables in the configured database  
- **Get Guide Tool**: DuckDB SQL syntax reference and performance tips
- Read Only: Connections established in [read-only mode](https://motherduck.com/docs/key-tasks/ai-and-motherduck/building-analytics-agents/#read-only-access) and in [SaaS mode](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#authentication-using-saas-mode) to restrict local file/database access within the remote MCP server
- Autoscaling: FastMCP Cloud with support for MotherDuck read scaling tokens (see [Autoscaling](#autoscaling))
- Query Timeout: 120 second timeout protection
- Result Limits: Max 1024 rows, 50,000 characters

## Quick Start

### Use the Deployed Server

MCP URL: `https://antm-hack-example.fastmcp.app/mcp`

For easy setup in **OpenAI SDK**, **Codex CLI**, **Claude Desktop**, **Claude Code**, **Cursor**, or **Gemini CLI**, go to:

👉 **[fastmcp.cloud/app/antm-hack-example](https://fastmcp.cloud/app/antm-hack-example)**

### Deploy Your Own Instance

1. Create a [MotherDuck account](https://app.motherduck.com/)

2. Create a [MotherDuck token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token)

3. Load data into MotherDuck (choose one):
   - Run `load_data.py` script to upload parquet files from `data/` directory
   - Or attach the [shared database](https://motherduck.com/docs/key-tasks/sharing-data/sharing-overview/#consuming-hidden-shares), by running: `ATTACH 'md:_share/antm_hack/88329567-1b97-4593-9696-73fd2be9c63d'`

4. Fork this repo (if not already done)

5. Go to [FastMCP Cloud](https://fastmcp.cloud)

6. Connect your repository

7. Set environment variable:
   ```
   MOTHERDUCK_TOKEN=<your_read_write_or_read_scaling_token>
   ```

8. Configure deployment settings:
   - Entrypoint: `motherduck_server.py`
   - Requirements File: `requirements.txt`

9. Deploy!

### Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export MOTHERDUCK_TOKEN="your_token_here"

# Run the server
fastmcp run motherduck_server.py
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MOTHERDUCK_TOKEN` | ✅ Yes | - | Your MotherDuck token (regular or read scaling) |
| `DATABASE_NAME` | No | antm_hack | Name of the MotherDuck database to connect to |
| `MAX_ROWS` | No | 1024 | Maximum rows in query results |
| `MAX_CHARS` | No | 50000 | Maximum characters in output |
| `QUERY_TIMEOUT` | No | 120 | Query timeout in seconds |

---

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

---

## The Dataset

The hackathon includes:
- **24 Parquet tables**: Structured retail data
- **19 JSONL log files**: Event streams  
- **Multiple PDFs**: Contracts, invoices, policies

Access it all via SQL queries to MotherDuck.

---

## Autoscaling

[FastMCP Cloud](https://fastmcp.cloud) autoscales and load balances traffic across multiple server instances based on demand. 

Each server instance picks a random session hint on startup for load distribution. With [MotherDuck read scaling tokens](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/read-scaling/), this enables concurrent queries across multiple read-only replicas for improved performance. With regular tokens, the session hint is a harmless no-op.

This architecture distributes load across both FastMCP instances and (optionally) MotherDuck read replicas.

---

## Links

- **Hackathon**: [github.com/TheoryVentures/antm](https://github.com/TheoryVentures/antm)
- **Competition Platform**: [hack.theoryvc.com](https://hack.theoryvc.com)
- **FastMCP**: [gofastmcp.com](https://gofastmcp.com/getting-started/welcome)
- **FastMCP Cloud**: [fastmcp.cloud](https://fastmcp.cloud)
- **MotherDuck**: [motherduck.com](https://motherduck.com)

---

## Files

```
.
├── motherduck_server.py    # Main FastMCP server
├── query_guide.md          # DuckDB SQL reference
├── requirements.txt        # Dependencies
└── README.md              # This file
```

---

**Built for [America's Next Top Modeler](https://github.com/TheoryVentures/antm) Hackathon**

---

_MIT License_
