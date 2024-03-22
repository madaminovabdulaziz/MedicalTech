from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MYSQL_HOST = 'monorail.proxy.rlwy.net'
MYSQL_DATABASE = "railway"
MYSQL_USER = "root"
MYSQL_PASSWORD = "mRMZCnONLDYxmNlMQVfcNEMCCWuZImvO"
MYSQL_PORT = 54193

connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = None

def get_engine():
    global engine
    if engine is None:
        engine = create_engine(connection_string, pool_size=100, max_overflow=100, pool_recycle=3600)
    return engine

Session = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = Session()
    try:
        yield db
    except exc.OperationalError as e:
        if e.orig.args[0] == 2006:  # MySQL server has gone away
            db.close()
            db = Session()
            yield db
        else:
            raise e
    finally:
        db.close()
