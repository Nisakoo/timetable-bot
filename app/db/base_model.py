from sqlalchemy import Integer, Column
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id!r})>"