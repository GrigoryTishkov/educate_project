import os, sys, logging, requests
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from models import metadata, raw_users_by_posts

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("extract")

API_URL = os.getenv("API_URL", "https://jsonplaceholder.typicode.com/posts")
DB_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

engine = create_engine(DB_DSN, pool_pre_ping=True)
metadata.create_all(engine)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(), retry=retry_if_exception_type(requests.RequestException))
def fetch_posts():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()

def upsert_posts(posts):
    with engine.begin() as conn:
        for p in posts:
            stmt = insert(raw_users_by_posts).values(
                post_id=p["id"], user_id=p["userId"], title=p.get("title"), body=p.get("body"), fetched_at=datetime.utcnow()
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["post_id"],
                set_={
                    "user_id": stmt.excluded.user_id,
                    "title": stmt.excluded.title,
                    "body": stmt.excluded.body,
                    "fetched_at": stmt.excluded.fetched_at,
                },
            )
            conn.execute(stmt)
    log.info("Затронуто %d постов", len(posts))

def main():
    try:
        posts = fetch_posts()
        upsert_posts(posts)
    except Exception as e:
        log.exception("Произошла ошибка: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()