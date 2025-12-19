import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.environ.get("DB_PATH", "data/bettenbutton.db")

# Ordner anlegen, falls nicht vorhanden
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

print("### DB_PATH =", DB_PATH)
print("### DB_URL  =", SQLALCHEMY_DATABASE_URL)
print("### DB_DIR_EXISTS =", os.path.isdir(os.path.dirname(DB_PATH)))
print("### DB_FILE_EXISTS =", os.path.isfile(DB_PATH))

# SQLite stabiler machen (wichtig bei Polling/Dashboard)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA busy_timeout=3000;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

