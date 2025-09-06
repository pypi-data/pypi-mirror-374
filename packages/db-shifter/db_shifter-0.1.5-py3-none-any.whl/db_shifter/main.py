import psycopg2
from psycopg2.extras import RealDictCursor, Json
from importlib.metadata import version as _pkg_version, PackageNotFoundError as _PkgNotFound
import sys
import argparse
from collections import defaultdict

# ===================== CLI OPTIONS ===================== #
parser = argparse.ArgumentParser(description="Move missing rows from old Postgres DB to new one.")
parser.add_argument("--old-db-url", required=True, help="Old DB connection string")
parser.add_argument("--new-db-url", required=True, help="New DB connection string")
parser.add_argument("--dry-run", action="store_true", help="Don't insert, just show what would happen")
parser.add_argument("--verbose", action="store_true", help="Print all operations in detail")
parser.add_argument("--table", help="Sync just one table")
parser.add_argument("--skip-fk", action="store_true", help="Ignore foreign key errors")
# Version flag
def _resolve_version():
    try:
        return _pkg_version("db-shifter")
    except _PkgNotFound:
        return "unknown"
parser.add_argument("--version", action="version", version=f"%(prog)s {_resolve_version()}")
args = parser.parse_args()

# === A log of all table activities to generate final summary === #
sync_log = defaultdict(lambda: {"existing_new": 0, "existing_old": 0, "inserted": 0, "inserted_pks": []})


def quote_table(name: str) -> str:
    """Safely quote a table name with double quotes."""
    return f'"{name}"'


def quote_ident(name: str) -> str:
    """Safely quote a column name or identifier."""
    return f'"{name}"'


def get_all_tablez(conn):
    """Fetch all tables in the public schema."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname='public'
        """)
        return [row[0] for row in cur.fetchall()]


def sniff_primary_key(conn, table_name):
    """Identify the primary key column of a table."""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{quote_table(table_name)}'::regclass
              AND i.indisprimary;
        """)
        res = cur.fetchone()
        return res[0] if res else None


def count_rows(conn, table_name):
    """Count number of rows in a table."""
    with conn.cursor() as cur:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {quote_table(table_name)}")
            return cur.fetchone()[0]
        except Exception:
            return 0


def pull_existing_ids(conn, table_name, pk):
    """Pull primary key values already in the new DB."""
    with conn.cursor() as cur:
        try:
            cur.execute(f"SELECT {quote_ident(pk)} FROM {quote_table(table_name)}")
            return set(row[0] for row in cur.fetchall())
        except Exception:
            return set()


def pull_missing_rows(conn, table_name, pk, existing_ids):
    """Get rows from old DB that are NOT present in new DB."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if not existing_ids:
            cur.execute(f"SELECT * FROM {quote_table(table_name)}")
        else:
            ids_tuple = tuple(existing_ids)
            cur.execute(
                f"SELECT * FROM {quote_table(table_name)} WHERE {quote_ident(pk)} NOT IN %s", 
                (ids_tuple,)
            )
        return cur.fetchall()


def push_rows_to_new(conn, table_name, rows, pk, dry_run=False, verbose=False):
    """Insert missing rows into the new DB, optionally as dry-run."""
    if not rows:
        return
    keys = rows[0].keys()

    with conn.cursor() as cur:
        for row in rows:
            if verbose:
                print(f"  🧬 {row}")
            if dry_run:
                continue
            # Adapt Python dict/list values (e.g., JSON/JSONB columns) for psycopg2
            def _adapt_value(value):
                if isinstance(value, (dict, list)):
                    return Json(value)
                return value

            vals = [_adapt_value(row[k]) for k in keys]
            placeholders = ','.join(['%s'] * len(vals))
            columns = ','.join([quote_ident(k) for k in keys])
            try:
                cur.execute(
                    f"INSERT INTO {quote_table(table_name)} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                    vals
                )
                sync_log[table_name]["inserted_pks"].append(row.get(pk))
                sync_log[table_name]["inserted"] += 1
            except Exception as e:
                if args.skip_fk:
                    print(f"  ⚠️  FK error skipped: {e}")
                else:
                    raise e

    if not dry_run:
        conn.commit()


def sync_em_all(conn_old, conn_new):
    """Main sync function for all or specified tables."""
    tables = [args.table] if args.table else get_all_tablez(conn_old)
    print(f"🗃️ Found {len(tables)} tables to process")

    for table in tables:
        print(f"\n🚀 Syncing: {table}")
        pk = sniff_primary_key(conn_old, table)
        if not pk:
            print(f"⚠️ Skipping {table} (no PK found)")
            continue

        existing_old = count_rows(conn_old, table)
        existing_new_ids = pull_existing_ids(conn_new, table, pk)
        existing_new = len(existing_new_ids)

        rows = pull_missing_rows(conn_old, table, pk, existing_new_ids)

        sync_log[table]["existing_old"] = existing_old
        sync_log[table]["existing_new"] = existing_new

        print(f"📊 Old DB Rows: {existing_old} | New DB Rows (before): {existing_new}")
        print(f"📥 {len(rows)} new rows to insert")

        try:
            push_rows_to_new(conn_new, table, rows, pk, dry_run=args.dry_run, verbose=args.verbose)
            print(f"✅ Done with {table}")
        except Exception as e:
            print(f"❌ Error syncing {table}: {str(e)}")

    # === FINAL TOXIC REPORT === #
    print("\n📦 Final Sync Report:")
    for table, stats in sync_log.items():
        status = "✅ CHANGED" if stats["inserted"] else "❌ UNCHANGED"
        print(f"\n🧾 Table: {table} --- {status}")
        print(f"   🔢 Old DB Rows: {stats['existing_old']}")
        print(f"   🔢 New DB Rows (before): {stats['existing_new']}")
        print(f"   ➕ Rows Added: {stats['inserted']}")
        if stats["inserted_pks"]:
            print(f"   🧬 PKs Added: {stats['inserted_pks']}")


# ===================== BOOM 💣 ===================== #
def main():
    conn_old = psycopg2.connect(args.old_db_url)
    conn_new = psycopg2.connect(args.new_db_url)

    try:
        sync_em_all(conn_old, conn_new)
    finally:
        conn_old.close()
        conn_new.close()
