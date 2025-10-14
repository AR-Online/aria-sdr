import os
import sys

try:
    import psycopg2  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - optional dependency for local checks
    psycopg2 = None  # type: ignore[assignment]
from dotenv import load_dotenv


def main() -> int:
    # Load .env with robust encoding handling
    try:
        load_dotenv()
    except UnicodeDecodeError:
        load_dotenv(encoding="latin-1")
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set in environment/.env", file=sys.stderr)
        return 2
    try:
        if psycopg2 is None:
            print(
                "psycopg2 não instalado; instale para testar a conexão (pip install psycopg2-binary)",
                file=sys.stderr,
            )
            return 3
        # Log minimal DSN info (mask password)
        print("Using DATABASE_URL with host:", url.split("@")[-1].split("/")[0])
        conn = psycopg2.connect(url)
        print("Connection successful!")
        with conn, conn.cursor() as cur:
            cur.execute("SELECT NOW();")
            row = cur.fetchone()
            if row is not None:
                print("Current Time:", row[0])
        print("Connection closed.")
        return 0
    except Exception as e:
        print(f"Failed to connect: {e}", file=sys.stderr)
        # Also print exception type for diagnostics
        print(f"Exception type: {type(e).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
