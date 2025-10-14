import os
import sys

try:
    import psycopg  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - optional dependency for local checks
    psycopg = None  # type: ignore[assignment]
from dotenv import load_dotenv


def main() -> int:
    try:
        load_dotenv()
    except UnicodeDecodeError:
        load_dotenv(encoding="latin-1")

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL not set in environment/.env", file=sys.stderr)
        return 2

    try:
        # Print host portion only (mask creds)
        print("Using DATABASE_URL host:", dsn.split("@")[-1].split("/")[0])

        if psycopg is None:
            print(
                "psycopg (psycopg3) não instalado; instale para testar a conexão (pip install psycopg)",
                file=sys.stderr,
            )
            return 3

        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute("select now();")
            now = cur.fetchone()[0]
            print("Current Time:", now)
        print("Connection successful and closed.")
        return 0
    except Exception as e:
        print(f"Failed to connect: {e}", file=sys.stderr)
        print(f"Exception type: {type(e).__name__}", file=sys.stderr)
        # psycopg3 exceptions may have sqlstate
        sqlstate = getattr(e, "sqlstate", None)
        if sqlstate:
            print(f"SQLSTATE: {sqlstate}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
