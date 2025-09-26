import os, sys, logging
from datetime import datetime
from sqlalchemy import create_engine, select, func
from sqlalchemy.dialects.postgresql import insert
from models import metadata, raw_users_by_posts, top_users_by_posts

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("transform")

DB_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

engine = create_engine(DB_DSN, pool_pre_ping=True)
metadata.create_all(engine)

def aggregate():
    with engine.begin() as conn:
        stmt = select(raw_users_by_posts.c.user_id, func.count().label("posts_cnt")).group_by(raw_users_by_posts.c.user_id)
        results = conn.execute(stmt).fetchall()
        for row in results:
            stmt_upsert = insert(top_users_by_posts).values(
                user_id=row.user_id, posts_cnt=row.posts_cnt, calculated_at=datetime.utcnow()
            )
            stmt_upsert = stmt_upsert.on_conflict_do_update(
                index_elements=["user_id"],
                set_={"posts_cnt": stmt_upsert.excluded.posts_cnt, "calculated_at": stmt_upsert.excluded.calculated_at},
            )
            conn.execute(stmt_upsert)
    log.info("Агрегировано %d пользователей", len(results))

def main():
    try:
        aggregate()
    except Exception as e:
        log.exception("Произошла ошибка: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()