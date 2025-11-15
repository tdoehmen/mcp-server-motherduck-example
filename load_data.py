"""
Load ANTM Hackathon Dataset into MotherDuck

This script loads all parquet files from the data/ directory into MotherDuck tables.

Usage:
    export MOTHERDUCK_TOKEN="your_token_here"
    python3 load_data.py
"""

import duckdb
import os
from pathlib import Path

# Configuration
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME", "antm_hack")

def load_parquet_files():
    """Load all parquet files from data/ directory into MotherDuck"""
    
    if not MOTHERDUCK_TOKEN:
        print("❌ Error: Please set MOTHERDUCK_TOKEN environment variable")
        print("   Example: export MOTHERDUCK_TOKEN='your_token_here'")
        return
    
    # Connect to MotherDuck
    print(f"🔌 Connecting to MotherDuck database: {DATABASE_NAME}")
    conn = duckdb.connect(
        f"md:{DATABASE_NAME}",
        config={'motherduck_token': MOTHERDUCK_TOKEN}
    )
    
    # Find data directory
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        print(f"❌ Error: data/ directory not found at {data_dir}")
        return
    
    # Find all parquet files
    parquet_files = list(data_dir.glob("*.parquet"))
    
    if not parquet_files:
        print("❌ No parquet files found in data/ directory")
        return
    
    print(f"📦 Found {len(parquet_files)} parquet files\n")
    
    # Load each parquet file as a table
    for parquet_file in sorted(parquet_files):
        table_name = parquet_file.stem  # filename without extension
        file_path = str(parquet_file.absolute())
        
        try:
            print(f"Loading {table_name}...", end=" ")
            
            # Create table from parquet file
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM '{file_path}'
            """)
            
            # Get row count
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            print(f"✅ {row_count:,} rows")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print(f"\n🎉 Data loading complete!")
    print(f"📊 Tables created in {DATABASE_NAME} database")
    
    # List all tables
    print("\n📋 Tables in database:")
    tables = conn.execute("""
        SELECT table_name, estimated_size 
        FROM duckdb_tables() 
        WHERE database_name = ? 
        ORDER BY table_name
    """, [DATABASE_NAME]).fetchall()
    
    for table_name, size in tables:
        print(f"  • {table_name}")
    
    conn.close()
    print("\n✅ Done!")

if __name__ == "__main__":
    load_parquet_files()

