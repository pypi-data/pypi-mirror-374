import argparse
import anyio

from nlbone.adapters.db.sqlalchemy.schema import init_db_async, init_db_sync

def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize database schema (create_all).")
    parser.add_argument("--async", dest="use_async", action="store_true", help="Use AsyncEngine")
    args = parser.parse_args()

    if args.use_async:
        anyio.run(init_db_async)
    else:
        init_db_sync()

if __name__ == "__main__":
    main()
