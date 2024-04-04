import pandas as pd
from sqlalchemy import create_engine, insert
from sqlalchemy import Table, Column, Integer, String, Float
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError

metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    Column("user_uid", String, primary_key=True),
)

event_table = Table(
    "popcorn_events",
    metadata_obj,
    Column("event_uid", Integer, primary_key=True, autoincrement=True),
    Column("user_uid", String),
    Column("popcorn_id_1", String),
    Column("popcorn_id_2", String),
    Column("score", Float),
    Column("timestamp", Integer),
)


def create_tables():
    engine = setup_connection(host="popcorn_db")
    user_table.create(engine, checkfirst=True)
    event_table.create(engine, checkfirst=True)
    engine.dispose()


def reset_tables():
    engine = setup_connection(host="popcorn_db")
    user_table.drop(engine, checkfirst=True)
    event_table.drop(engine, checkfirst=True)
    create_tables()
    engine.dispose()


def setup_connection(user='popcorn', password='popcornegott', host='popcorn_db'):
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:5432/popcorn")
    return engine


def add_user(user_uid: str) -> None:
    engine = setup_connection(host="popcorn_db")
    with engine.connect() as conn:
        try:
            conn.execute(
                insert(user_table).values(user_uid=user_uid)
            )
            conn.commit()
        except IntegrityError as e:
            print(f"User {user_uid} already exists")
    engine.dispose()


def add_event(user_uid: int, popcorn_id_1: str, popcorn_id_2: str, score: float, timestamp: int) -> None:
    engine = setup_connection(host="popcorn_db")
    with engine.connect() as conn:
        conn.execute(
            insert(event_table).values(user_uid=user_uid, popcorn_id_1=popcorn_id_1, popcorn_id_2=popcorn_id_2, score=score, timestamp=timestamp)
        )
        conn.commit()
    engine.dispose()


def read_table() -> pd.DataFrame:
    engine = setup_connection(host="popcorn_db")
    df = pd.read_sql_table("popcorn_events", engine)
    engine.dispose()
    return df


if __name__ == "__main__":
    engine = setup_connection(host="localhost")

    reset_tables()
    add_user("zxc")
    add_user("asd")
    add_user("asd")

    add_event("zxc", "1", "2", 0.5, 123)

    print(read_table())
