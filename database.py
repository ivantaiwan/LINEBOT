from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    date = Column(DateTime)
    time = Column(String)
    fee = Column(Integer)
    participants = Column(Integer)
    users = Column(String)  # We'll store user names as a comma-separated string

Base.metadata.create_all(bind=engine)