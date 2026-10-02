"""Create the tracked tables/view inside an existing empty demo database."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from db import get_conn


def bootstrap():
    source = (ROOT / "sql/schema.sql").read_text()
    source = '\n'.join(line for line in source.splitlines() if not line.lstrip().startswith('--'))
    with get_conn() as conn:
        cursor = conn.cursor()
        try:
            for statement in source.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            conn.commit()
        finally:
            cursor.close()


if __name__ == '__main__':
    bootstrap()
    print('Academic demo schema created or already present.')
