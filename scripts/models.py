from sqlalchemy import Table, Column, Integer, Text, DateTime, MetaData
from datetime import datetime


metadata = MetaData()


raw_users_by_posts = Table(
"raw_users_by_posts",
metadata,
Column("post_id", Integer, primary_key=True),
Column("user_id", Integer, nullable=False),
Column("title", Text),
Column("body", Text),
Column("fetched_at", DateTime, default=datetime.utcnow),
)


top_users_by_posts = Table(
"top_users_by_posts",
metadata,
Column("user_id", Integer, primary_key=True),
Column("posts_cnt", Integer, nullable=False),
Column("calculated_at", DateTime, nullable=False),
)