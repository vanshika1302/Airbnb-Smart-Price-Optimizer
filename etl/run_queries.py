"""
run_queries.py
---------------
Runs each statement in sql/analysis_queries.sql against the warehouse,
prints the result, and saves it as a CSV under data/processed/query_results/
so results can be dropped straight into the README or a slide.

Usage:
    python etl/run_queries.py
"""

import re
from pathlib import Path

from warehouse import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "sql" / "analysis_queries.sql"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "query_results"


def split_statements(sql_text: str):
    """Split into (label, statement) pairs using the '-- Q<n>.' comment as the label."""
    blocks = re.split(r"(?=-- Q\d+\.)", sql_text)
    statements = []
    for block in blocks:
        block = block.strip()
        if not block.startswith("-- Q"):
            continue
        label_match = re.match(r"-- (Q\d+)\.\s*(.*)", block)
        label = label_match.group(1) if label_match else "Q?"
        title = label_match.group(2) if label_match else block[:40]
        sql = block.split("\n", 1)[1] if "\n" in block else ""
        sql = sql.strip().rstrip(";")
        if sql:
            statements.append((label, title, sql))
    return statements


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = get_connection()
    sql_text = SQL_PATH.read_text()

    for label, title, stmt in split_statements(sql_text):
        print("\n" + "=" * 70)
        print(f"{label}: {title}")
        print("=" * 70)
        df = con.execute(stmt).fetchdf()
        print(df.to_string(index=False))
        out_path = OUT_DIR / f"{label.lower()}.csv"
        df.to_csv(out_path, index=False)

    con.close()
    print(f"\nAll query results saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
