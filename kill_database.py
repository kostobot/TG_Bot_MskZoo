import sys
import logging
from database.models import Base
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

engine = create_engine(f"sqlite:///database_bot.db")
Base.metadata.drop_all(bind=engine)
logging.info('База данных удалена')