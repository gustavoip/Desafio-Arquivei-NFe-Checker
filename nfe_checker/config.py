import logging
from logging.handlers import RotatingFileHandler

from flask_sqlalchemy import SQLAlchemy, sqlalchemy, orm


def create_logger() -> logging.Logger:
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

    handler = RotatingFileHandler(
        filename="nfes.log", backupCount=3, maxBytes=5 * 1024 * 1024
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


engine = sqlalchemy.create_engine('sqlite:///foo.db')
Session = orm.sessionmaker(bind=engine)

logger = create_logger()
db = SQLAlchemy()
