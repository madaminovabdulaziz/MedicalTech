from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MYSQL_HOST = 'monorail.proxy.rlwy.net'
MYSQL_DATABASE = "railway"
MYSQL_USER = "root"
MYSQL_PASSWORD = "mRMZCnONLDYxmNlMQVfcNEMCCWuZImvO"
MYSQL_PORT = 54193

connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine = create_engine(connection_string, pool_size=100, max_overflow=100)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
