from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True,index=True,nullable=False)
    fitness_valid = Column(Boolean)
    open_job_card = Column(Boolean)
    cleaning_completed = Column(Boolean)
    sensor_alert=Column(Boolean,default=False)
    # parking_slot = Column(Integer, nullable=True)
    mileage = Column(Float)
    branding_priority = Column(Integer)
    override_status=Column(String,nullable=True)


from sqlalchemy import DateTime
from datetime import datetime
import json

class InductionLog(Base):
    __tablename__ = "induction_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    traffic_level = Column(Integer)
    service_trains = Column(String)
    standby_trains = Column(String)
    maintenance_trains = Column(String)