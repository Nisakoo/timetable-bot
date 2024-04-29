from sqlalchemy import Integer, String, Column, Text
from sqlalchemy.orm import relationship, backref

from app.db.base_model import BaseModel


class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String(256))
    timetable = Column(Text)
    additional_info = Column(Text)
    address = Column(String(256))

    def name_block(self):
        return f"<b>{self.name}</b>\n\n"
    
    def timetable_block(self):
        return f"{self.timetable}"
    
    def additional_info_block(self):
        if (self.additional_info is not None):
            return f"\n\n<blockquote>{self.additional_info}</blockquote>"
        
        return str()
    
    def address_block(self):
        if self.address is not None:
            return f"\n\n{self.address}"
        
        return str()

    def __repr__(self):
        s = self.name_block()
        s += self.timetable_block()
        s += self.additional_info_block()
        s += self.address_block()

        return s