from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base_model import BaseModel
from app.models.organization import Organization


class SqliteDataBase:
    def __init__(self, db_url: str):
        self.__db_url = db_url

        self.__engine = create_engine(self.__db_url)
        BaseModel.metadata.create_all(self.__engine)

        self.__session = Session(self.__engine)
        self.__session.connection()

    def add_organization(
            self,
            name: str,
            timetable: str,
            additional_info: str = None,
            address: str = None
        ):
        self.__session.add(
            Organization(
                name=name,
                timetable=timetable,
                additional_info=additional_info,
                address=address
            )
        )
        self.commit()

    def get_organizations(self):
        return self.__session.query(Organization).all()
    
    def get_organization_by_id(self, id: int):
        return self.__session.query(Organization).get(id)
    
    def get_organization_by_name(self, name: str):
        return self.__session.query(Organization).filter(Organization.name == name).first()
    
    def delete_by_id(self, id: int):
        self.__session.query(Organization).filter(Organization.id == id).delete()
        self.commit()

    def update_addinfo(self, org: Organization, addinfo: str):
        org.additional_info = addinfo
        self.commit()
    
    def commit(self):
        self.__session.commit()