from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = f"postgresql://sim_postgresuser:simulation$dev#5432@sim-postgres-instance.crwwqoc0iape.us-west-2.rds.amazonaws.com:5432/entity_store"


db_engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(autocommit=False, autoflush=True, bind=db_engine)


def create_tables():
    Base.metadata.create_all(bind=db_engine)


def drop_tables():
    Base.metadata.drop_all(db_engine)
