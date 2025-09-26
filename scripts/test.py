import pytest
from sqlalchemy import create_engine, select
from extract import upsert_posts
from models import raw_users_by_posts


@pytest.fixture()
def test_engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(autouse=True)
def setup_table(test_engine):
    raw_users_by_posts.create(test_engine)
    yield
    raw_users_by_posts.drop(test_engine)


@pytest.fixture()
def sample_post():
    return [
        {
            "id": 1,
            "userId": 101,
            "title": "First Post",
            "body": "Content of first post"
        },
        {
            "id": 2,
            "userId": 102,
            "title": "Second Post",
            "body": "Content of second post"
        }
    ]


@pytest.fixture()
def update_post():
    return [
        {
            "id": 1,
            "userId": 101,
            "title": "First Best Post",
            "body": "Updated Content of first post"
        },
        {
            "id": 3,
            "userId": 102,
            "title": "Second Post",
            "body": "Content of second post"
        }
    ]


def test_insert_sample_post(test_engine, sample_post):
    upsert_posts(sample_post)

    with test_engine.connect() as conn:
        result = conn.execute(select(raw_users_by_posts)).fetchall()

        assert len(result) == 2
        post = next((r for r in result if r.post_id == 1), None)
        assert post.post_id == 1
        assert post.user_id == 101
        assert post.title == "First Post"
        assert post.body == "Content of first post"
        assert post.fetched_at is not None

def test_update_sample_post(test_engine, sample_post, update_post):
    upsert_posts(sample_post)

    with test_engine.connect() as conn:
        origin_fetched_at = conn.execute(select(
            raw_users_by_posts.c.fetched_at).where(
            raw_users_by_posts.c.post_id == 1)).scalar()

    upsert_posts(update_post)

    with test_engine.connect() as conn:
        result = conn.execute(select(raw_users_by_posts).order_by(raw_users_by_posts.c.post_id)).fetchall()

        assert len(result) == 3
        updated_post = next((r for r in result if r.post_id == 1), None)
        assert updated_post.title == "First Best Post"
        assert updated_post.body == "Updated Content of first post"
        assert updated_post.fetched_at > origin_fetched_at

        uncharted_post = next((r for r in result if r.post_id == 2), None)
        assert uncharted_post.title == "Second Post"


def test_upsert_empty_list(test_engine):
    upsert_posts([])

    with test_engine.connect() as conn:
        result = conn.execute(select(raw_users_by_posts)).fetchall()

        assert len(result) == 0


def test_upsert_duplicate(test_engine):

    duplicate_posts = [
        {"id": 1, "userId": 101, "title": "First"},
        {"id": 1, "userId": 101, "title": "Duplicate"}
    ]

    upsert_posts(duplicate_posts)

    with test_engine.connect() as conn:
        result = conn.execute(select(raw_users_by_posts)).fetchall()

        assert len(result) == 1
        assert result[0].title == "Duplicate"


