
from dbflux import Sqlite,BaseDB,DBModel
from sqlalchemy import  Column, Integer, Boolean,String,DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime,timezone
import json
Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)






class Account(Base):
    __tablename__   = "sessions"
    session_id      = Column(String, primary_key=True)
    phone           = Column(String, default="")
    user_id         = Column(Integer, default=0)  
    username        = Column(String, default="") 
    first_name      = Column(String, default="") 
    last_name       = Column(String, default="") 
    password        = Column(String, default="") 
    
    dc_id           = Column(Integer, default=0)
    api_id          = Column(Integer, default=0)  
    api_hash        = Column(String, default="")
    device_model    = Column(String, default="") 
    system_version  = Column(String, default="") 
    app_version     = Column(String, default="") 
    
    session         = Column(String, default='')
    created_at      = Column(DateTime, default=utc_now)
    device_name     = Column(String, default="")  
    status          = Column(String, default="") 
    is_bot          = Column(Boolean, default=False)
              
   
   
    
    
      

    def __init__(self, session_id:str,phone :str='',user_id=0,first_name="", 
                username="", last_name="", password="",dc_id=0, api_id=0, 
                api_hash="",device_model="", system_version="", app_version="", 
                session  ='',device_name="",is_bot=False, status= ""):
        
        self.session_id     = session_id
        self.phone          = phone
        self.user_id        = user_id
        self.username       = username
        self.first_name     = first_name
        self.last_name      = last_name
        self.password       = password
        self.dc_id          = dc_id
        self.api_id         = api_id
        self.api_hash       = api_hash
        self.device_model   = device_model
        self.system_version = system_version
        self.app_version    = app_version
        self.session        = session
        self.device_name      = device_name
        self.status         = status
        self.is_bot         = is_bot

    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  
    
    def __repr__(self):
        return f"{self.__class__.__name__}({", ".join(f"{key}={value!r}" for key, value in self.to_dict().items())})"
    
    def __str__(self):
        return json.dumps(self.to_dict(),indent=4,ensure_ascii=False)



class Storage(DBModel):
    def __init__(self,base_db:'BaseDB'=Sqlite(db_name="sessions.ses")):
        """
        Initialize the storage object.

        Args:
            base_db (BaseDB): The base for the model. Defaults to a Sqlite database
                with the name "sessions.ses".
        """
        super().__init__(Account,base_db)
        self.create_tables(Base)